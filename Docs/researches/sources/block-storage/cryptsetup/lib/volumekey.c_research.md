# File Research: sources/block-storage/cryptsetup/lib/volumekey.c

## Purpose
Implements `struct volume_key` allocation, ownership, metadata, linked-list management, generation, and kernel-key upload/drop helpers.

## Key Responsibilities
- Allocates volume keys with safe memory for key bytes.
- Converts existing safe allocations into volume-key ownership.
- Replaces a volume key’s safe allocation with caller-provided safe memory.
- Provides accessors for key bytes, key length, id, description, keyring type, and linked-list next pointer.
- Adds keys to linked lists and finds keys by id.
- Frees entire linked lists, wiping key bytes.
- Generates random, normal, or empty quality volume keys.
- Uploads volume keys into the thread kernel keyring and drops uploaded keys.

## Important Details
- Key length zero is valid and represents no key bytes.
- Newly allocated keys start with `KEY_NOT_VERIFIED`, invalid keyring type, and key id `-1`.
- Description strings are owned copies.
- Kernel-key upload requires key bytes, description, and valid keyring type.

## Dependencies
Uses safe memory, random generation, keyring helpers, and internal cryptsetup unlink wrappers.
