# File Research: sources/block-storage/libblkid-rs/src/encode.rs

Purpose: Exposes libblkid string encoding helpers.

Key APIs:
- `encode_string`
- `safe_string`

Implementation notes:
- Shared helper allocates a buffer, calls the supplied C encoder, truncates at the first NUL, and converts to Rust `String`.
- Includes unit tests for basic escaping and whitespace replacement.

Notable risks:
- Buffer size is `string.len() * 4`; a fully escaped string may need an extra byte for the terminating NUL.
- Empty input creates a zero-length output buffer, which may fail even if libblkid would otherwise encode an empty string.
- Any nonzero C return is reported as `InvalidConv`.
