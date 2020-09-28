# import the api
from json import dump
from os import scandir
from random import uniform
from time import sleep, time

import api
from locations import NORWAY

MAX_PROFILES = 5

def on_message(message, profileid, _type):
    # type: text, image, tap
    # do stuff with message
    print(_type + " " + message)


if __name__ == '__main__':
    tokens = api.fullLogin()

    profiles = api.fetchProfiles(
        tokens[0],
        **NORWAY,
    )['profiles']

    # LOAD PROFILES ALREADY MESSAGE TO NOT SPAM THEM
    messaged = set()
    for item in scandir('data/messaged'):
        if item.is_file():
            messaged.add(item.name.split(".json")[0])
    print(f"Known profiles: {messaged}")

    start_time = time()
    total_sent = 0

    socket = api.messageSocket(tokens, on_message)
    socket.start()

    for profile in profiles[:MAX_PROFILES]:
        try:
            profile_id = profile['profileId']
            if profile_id not in messaged:
                # SEND MESSAGE
                print(f"Sending message to profile: {profile_id}")
                socket.message(profile_id, "Hi")

                # SAVE PROFILE ID
                with open(f'data/messaged/{profile_id}.json', 'w') as outfile:
                    dump(profile, outfile)

                total_sent += 1

                # WAIT TO NOT SPAM
                wait_time = uniform(2, 4)
                print(f"Waiting {wait_time} seconds...")
                sleep(wait_time)

                # TODO: If you get messages and not ack it will close to socket
                # If you wait here on message it will block the loop
                # Need to figure it out (Probably add TIMEOUT decorator on check_messages)
                socket.check_messages()
            else:
                print(f"Skipping known profile: {profile_id}")
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            print(f"Total Time: {time()-start_time}")
            print(f"Total Sent: {total_sent}")
