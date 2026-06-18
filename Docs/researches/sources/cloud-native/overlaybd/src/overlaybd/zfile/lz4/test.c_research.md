## sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/test.c

Purpose: minimal C example/test for the vendored LZ4 API. It compresses a static string with `LZ4_compress_default`, decompresses it with `LZ4_decompress_safe`, and validates byte-for-byte equality.

Important functions: `run_screaming` prints an error and exits. `main` computes `src_size`, allocates `LZ4_compressBound(src_size)`, checks the returned compressed size, shrinks the allocation with `realloc`, allocates a regeneration buffer, decompresses, and validates with `memcmp`.

Control flow: the test is linear and intentionally demonstrates return-code handling. Compression failure is treated as size 0 or negative; decompression failure is negative; successful decompression must return a positive byte count. It frees compressed storage before validation but never explicitly frees `regen_buffer` before process exit.

State/persistence: all state is heap memory in one process; no files are created. Dependencies are `lz4.h`, `stdio.h`, `string.h`, and `stdlib.h`.

Integration points: useful as a smoke test for the vendored LZ4 source, but it does not exercise streaming, dictionaries, partial decode, malformed input, or OverlayBD zfile metadata. Risks/test gaps: static input is tiny and highly narrow; it cannot catch block-boundary bugs, unsafe decode misuse, or performance regressions. Higher-level zfile tests provide stronger integration coverage.
