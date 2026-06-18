# File Research: sources/block-storage/libcryptsetup-rs/src/macros.rs

Defines core crate macros for synchronization, error mapping, pointer conversion, string conversion, enum conversion, C strings, and callback shims.

Key macros:
- `mutex!`
- `errno!`
- `errno_int_success!`
- `int_to_return!`
- `try_int_to_return!`
- `ptr_to_option!`
- `ptr_to_option_with_reference!`
- `ptr_to_result!`
- `ptr_to_result_with_reference!`
- `path_to_cstring!`
- `to_cstring!`
- `to_byte_ptr!`
- `to_mut_byte_ptr!`
- `from_str_ptr!`
- `from_str_ptr_to_owned!`
- `consts_to_from_enum!`
- `c_str!`
- `c_confirm_callback!`
- `c_logging_callback!`
- `c_progress_callback!`
- token handler callback macros

Behavior:
- `mutex!` wraps unsafe libcryptsetup calls and enforces either feature-gated locking or single-thread use.
- `errno!` treats negative values as errno, zero as success, and positive values as panic.
- `errno_int_success!` treats negative values as errno and non-negative as returned success value.
- Pointer macros centralize null-to-option/result behavior.
- Callback macros convert raw C callback inputs into Rust values and optional user data references.

Research notes:
- `path_to_cstring!` uses `Path::to_str`, so non-UTF-8 paths are rejected.
- Callback macros can panic on invalid strings or log levels in some cases.
- The token handler open macro appears internally inconsistent in the read source: it declares `Result<Box<[u8]>, LibcryptErr>` but matches `Ok(())`, and references `$crate::SizeT` while the crate re-exports `size_t`.
- Unit tests cover callback wrappers, enum conversion macro, and no-mutex multi-thread panic.
