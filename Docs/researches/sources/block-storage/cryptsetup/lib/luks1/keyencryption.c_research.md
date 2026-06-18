# File Research: sources/block-storage/cryptsetup/lib/luks1/keyencryption.c

This file implements encrypted access to LUKS1 keyslot storage.

Core behavior:
- `_error_hint` logs actionable errors when dm-crypt or userspace crypto cannot use the requested cipher/mode/key size, including XTS key-size and cipher-spec format hints.
- `LUKS_endec_template` is the fallback path that creates a private temporary dm-crypt mapping named `temporary-cryptsetup-<pid>` over the metadata device:
  - Computes keyslot-aligned size from block size and `LUKS_ALIGN_KEYSLOTS`.
  - Uses `CRYPT_ACTIVATE_PRIVATE`, and read-only flag for decrypt.
  - Builds cipher spec from cipher and mode.
  - Adjusts block-device access and verifies write permissions.
  - Creates a dm-crypt target over the metadata device at the requested sector.
  - Opens the temporary mapper path with `O_DIRECT | O_SYNC`.
  - Invokes either blockwise read or write callback.
  - Removes the temporary mapping with forced deactivation.
- `LUKS_encrypt_to_storage`:
  - Requires sector-aligned input length.
  - First tries the userspace crypto wrapper through `crypt_storage_init` and `crypt_storage_encrypt`.
  - Falls back to temporary dm-crypt if the wrapper reports unsupported or missing cipher support.
  - Writes encrypted data to the metadata device with blockwise aligned IO and syncs the device.
- `LUKS_decrypt_from_storage`:
  - Requires sector-aligned destination length.
  - First tries userspace crypto.
  - Falls back to temporary dm-crypt on unsupported/missing cipher support.
  - Reads encrypted keyslot data from the metadata device, reports too-small devices where detectable, then decrypts in memory.

Filesystem/block-storage relevance:
- This code is the LUKS1 keyslot IO path for reading and writing encrypted key material on disk.
- It bridges filesystem-style aligned IO constraints, raw block-device sector offsets, and dm-crypt/userspace crypto mechanisms.

Important notes:
- Only whole 512-byte sector reads/writes are accepted.
- The temporary dm-crypt mapping is private and forcibly removed on cleanup.
- Device locking is respected through `device_is_locked` and `device_open_locked`.
- IO failures during keyslot encryption/decryption are normalized to `-EIO` with user-facing log messages.
