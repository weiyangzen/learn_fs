# File Research: sources/block-storage/devicemapper-rs/src/core/util.rs

## Purpose
Provides low-level alignment, C-string, and C-struct byte-slice helpers.

## Key APIs
`align_to`, `byte_slice_from_c_str`, `str_from_c_str`, `str_from_byte_slice`, `mut_slice_from_c_str`, `slice_from_c_struct`, and `c_struct_from_slice`.

## Behavior
`align_to` rounds up to a power-of-two boundary. String helpers scan to first NUL and require UTF-8. Struct helpers use unsafe pointer casts to expose raw bytes or typed references.

## Notes
Safety relies on callers passing valid in-memory C structs and correctly-sized kernel buffers.
