# File Research: sources/block-storage/libcryptsetup-rs/src/tests/reencrypt.rs

Integration-style LUKS2 reencryption test.

Key entry point:
- `test_reencrypt_by_password`

Behavior:
- Creates a LUKS2 AES-XTS loopback device.
- Adds an initial key.
- Adds a new unbound/no-segment key using `CryptVolumeKey::NO_SEGMENT`.
- Activates the device.
- Reads current sector size, cipher, and cipher mode.
- Initializes reencryption with checksum resilience and SHA-256 hash.
- Runs `reencrypt2`.
- Deactivates mapper device.

Research notes:
- Requires `cryptsetup24supported`.
- Exercises `CryptParamsReencrypt`, nested `CryptParamsLuks2`, activation, keyslot, status, sector size, and reencryption APIs together.
