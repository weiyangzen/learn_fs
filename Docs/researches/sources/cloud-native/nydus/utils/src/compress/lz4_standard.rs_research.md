# sources/cloud-native/nydus/utils/src/compress/lz4_standard.rs

Purpose: low-level LZ4 block compression/decompression wrappers over `lz4_sys`.

Important APIs/types/functions: `lz4_compress(src) -> Result<Vec<u8>>` calls `LZ4_compressBound` and `LZ4_compress_default`. `lz4_decompress(src, dst) -> Result<usize>` validates destination size and calls `LZ4_decompress_safe`.

Control flow: compression rejects inputs too large for LZ4's i32 API or invalid compression bounds, allocates a destination buffer with capacity equal to the bound, calls the C API, sets vector length to returned compressed size, and returns it. Decompression rejects destination buffers at or above `i32::MAX`, validates the requested size with `LZ4_compressBound`, calls safe decompression, and maps negative return to IO error.

State and persistence: no state; all buffers are caller/local memory.

Dependencies and integration points: used by `compress/mod.rs` for `Algorithm::Lz4Block`. Depends on `libc::c_char`, `lz4_sys`, and crate error macros.

Risks: uses unsafe FFI and `Vec::set_len`; correctness depends on LZ4 respecting the supplied capacity. The test allocates a `u32::MAX`-sized vector to trigger errors, which may be too memory-heavy for some environments. No streaming LZ4 support here.

Test signals: boundary error test checks oversized compression/decompression input handling. Round-trip tests for LZ4 live in `compress/mod.rs`.
