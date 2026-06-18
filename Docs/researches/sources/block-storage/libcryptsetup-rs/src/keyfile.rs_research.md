# File Research: sources/block-storage/libcryptsetup-rs/src/keyfile.rs

Implements keyfile reading support.

Key types:
- `CryptKeyfileContents`
- `CryptKeyfileHandle<'a>`

Key API:
- `CryptKeyfileHandle::device_read`

Behavior:
- Reads a keyfile into libcryptsetup-allocated safe memory.
- Wraps returned pointer and length in `SafeMemHandle`.
- `CryptKeyfileContents` exposes bytes via `AsRef<[u8]>`.
- If key size is omitted, uses filesystem metadata length.

Research notes:
- This file depends on the crate’s special memory cleanup path described in `lib.rs`.
- The returned key material is automatically freed and safe-zeroed through `SafeMemHandle`.
