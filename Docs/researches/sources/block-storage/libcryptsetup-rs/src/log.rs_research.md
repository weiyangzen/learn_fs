# File Research: sources/block-storage/libcryptsetup-rs/src/log.rs

Provides global logging functions.

Key API:
- `log`
- `set_log_callback`

Behavior:
- `log` converts message to `CString` and calls `crypt_log` with null device pointer.
- `set_log_callback` registers a C callback and optional user data pointer globally.

Research notes:
- Callback type is an unsafe extern C function.
- User data is passed as raw `*mut c_void`; lifetime safety is the caller’s responsibility.
