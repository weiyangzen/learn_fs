# File Research: sources/block-storage/libcryptsetup-rs/src/wipe.rs

Implements wipe operations.

Key type:
- `CryptWipeHandle<'a>`

Key API:
- `wipe`

Behavior:
- Wraps `crypt_wipe`.
- Accepts device path, wipe pattern, offset, length, block size, flags, optional progress callback, and optional user data.
- Converts device path to C string and user data to `*mut c_void`.

Research notes:
- Progress callback is an unsafe extern C function.
- User data lifetime and callback safety are caller-managed.
