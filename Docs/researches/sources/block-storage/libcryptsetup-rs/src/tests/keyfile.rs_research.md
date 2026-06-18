# File Research: sources/block-storage/libcryptsetup-rs/src/tests/keyfile.rs

Tests keyfile memory cleanup behavior.

Key entry point:
- `test_keyfile_cleanup`

Behavior:
- Creates a temporary keyfile with known contents.
- Reads it through `CryptKeyfileHandle::device_read`.
- Checks returned bytes match expected password.
- Drops `CryptKeyfileContents`, then inspects the old pointer range to verify the cleartext is no longer present.

Research notes:
- This test directly targets `SafeMemHandle` cleanup semantics for keyfile material.
- It intentionally reads from a dangling pointer after drop for cleanup verification, which is unsafe test logic.
