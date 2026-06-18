# File Research: sources/block-storage/cryptsetup/lib/loopaes/loopaes.c

This file implements loop-AES-compatible keyfile parsing and activation.

Key behavior:
- Selects default hash by output key size: 16 bytes -> `sha256`, 24 bytes -> `sha384`, 32 bytes -> `sha512`.
- Applies loop-AES tweak bytes based on key count: 64 keys uses `0x55`, 65 keys uses `0xF4`, otherwise `0x00`.
- Hashes each input key line into a fixed-size output key component, XORs the first byte with the tweak, concatenates all components, and wraps the result as a `volume_key`.
- Detects ASCII-armored GPG keyfiles by scanning the start of the buffer for `BEGIN PGP MESSAGE`; encrypted GPG keyfiles are rejected with a user hint to decrypt externally.
- Normalizes `\n` and `\r` to NUL, then parses one, 64, or 65 NUL-separated key entries. All parsed keys must have the same nonzero length and be terminated.
- Activates a loop-AES-compatible dm-crypt mapping:
  - One key uses `<base_cipher>-cbc-plain64` and requires plain64 support.
  - Multi-key mode uses `<base_cipher>:64-cbc-lmk` and requires LMK support.
  - Device size and flags are adjusted through `device_block_adjust`.
  - The DM target is created through `dm_crypt_target_set` and `dm_create_device`.

Filesystem/block-storage relevance:
- Provides compatibility for legacy loop-AES encrypted block devices.
- Activation produces a live dm-crypt block mapping using cryptsetup’s regular device-mapper backend.

Important notes:
- `LOOPAES_KEYS_MAX` is 65, matching accepted keyfile layouts.
- Unsupported kernel capabilities are reported as inability to support loop-AES-compatible mapping.
