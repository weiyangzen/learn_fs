# File Research: sources/block-storage/cryptsetup/lib/loopaes/loopaes.h

This header declares the loop-AES compatibility interface.

It defines:
- Forward declarations for `struct crypt_device` and `struct volume_key`.
- `LOOPAES_KEYS_MAX` as 65.
- `LOOPAES_parse_keyfile`, which parses keyfile data into a `volume_key`, optional hash override, and key count.
- `LOOPAES_activate`, which activates a loop-AES-compatible mapping from a base cipher, key count, volume key, and activation flags.

Filesystem/block-storage relevance:
- This is the private interface used by cryptsetup’s loop-AES format support to turn keyfile material into a dm-crypt block mapping.
