# File Research: sources/block-storage/libcryptsetup-rs/src/tests/encrypt.rs

Integration-style encryption tests using loopback devices.

Key helpers:
- `init`
- `init_null_cipher`
- `init_by_keyfile`
- `activate_without_explicit_format`
- `activate_by_passphrase`
- `create_keyfile`
- `activate_by_keyfile`
- `activate_null_cipher`
- `write_random`
- `test_existence`
- `run_plaintext_test`

Test entry points:
- `test_encrypt_by_password`
- `test_encrypt_by_keyfile`
- `test_encrypt_by_password_without_explicit_format`
- `test_unencrypted`

Behavior:
- Creates LUKS2 AES-XTS devices, adds keyslots, activates mapper devices, writes random plaintext through mapper, then scans backing storage for plaintext.
- Negative encryption tests expect plaintext not to appear in backing file.
- Null cipher test expects plaintext to be visible.
- Uses mmap scanning with 1 MiB sliding window.
- Cleans up mapper device when `DO_CLEANUP` allows.

Research notes:
- Tests require root and loopback support through shared loopback harness.
- The keyfile path is derived from the loopback backing file path with `-key`.
