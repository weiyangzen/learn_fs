# File Research: sources/block-storage/libcryptsetup-rs/src/err.rs

Defines crate-wide error type `LibcryptErr`.

Variants:
- `IOError`
- `UuidError`
- `NullError`
- `Utf8Error`
- `JsonError`
- `InvalidConversion`
- `NullPtr`
- `NoNull`
- `Other`

Behavior:
- Implements `Display` and `std::error::Error`.
- Negative libcryptsetup return codes are generally mapped to `IOError` with raw OS errno.
- Conversion failures use explicit variants.

Research notes:
- `Other(String)` is used by tests and wrappers for ad hoc errors.
- The error type preserves the major boundary categories: OS/libcryptsetup errno, string/JSON/UUID conversion, null pointers, and invalid enum/flag conversions.
