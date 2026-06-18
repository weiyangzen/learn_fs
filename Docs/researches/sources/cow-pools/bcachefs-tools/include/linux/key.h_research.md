# File Research: sources/cow-pools/bcachefs-tools/include/linux/key.h

This header defines minimal keyring structures for user-space use. `struct user_key_payload` stores a data length and flexible payload, and `struct key` contains an atomic usage counter, serial, semaphore, and embedded payload.

`user_key_payload()` returns the embedded payload. `key_get()` increments usage when non-null, and `key_put()` decrements usage and frees the key when the counter reaches zero.
