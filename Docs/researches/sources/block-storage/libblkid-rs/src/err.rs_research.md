# File Research: sources/block-storage/libblkid-rs/src/err.rs

Purpose: Defines the crate-wide error type and `Result` alias.

Key APIs:
- `pub type Result<T> = std::result::Result<T, BlkidErr>`
- `BlkidErr` variants for FFI conversion, I/O, UTF-8, UUID, libblkid codes, and generic messages.

Implementation notes:
- `from_err!` generates `From` conversions for common standard-library errors.
- Implements `Display` and `std::error::Error`.

Notable risks:
- `uuid::Error` and `std::ffi::IntoStringError` are represented but do not have generated `From` implementations.
- `LibErr(0)` is used by `errno_ptr!` for null pointers, even though zero is not an actual negative libblkid error code.
- `PositiveReturnCode` assumes APIs wrapped by `errno!` should only return `0` or negative values.
