# File Research: sources/block-storage/libcryptsetup-rs/src/debug.rs

Defines one public debug helper.

Key API:
- `set_debug_level(level: CryptDebugLevel)`

Behavior:
- Converts `CryptDebugLevel` into the C integer value and calls `crypt_set_debug_level`.

Research notes:
- This is global libcryptsetup state.
- No result is returned because the underlying API does not expose one here.
