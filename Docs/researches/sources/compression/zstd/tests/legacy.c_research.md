<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/legacy.c -->
## sources/compression/zstd/tests/legacy.c

Purpose: Verifies libzstd can decode hard-coded frames produced by legacy zstd versions `v0.4.3` through `v0.8.0`.

Important APIs and functions: `testSimpleAPI()` uses `ZSTD_decompress` and `ZSTD_getErrorName`. `testStreamingAPI()` uses `ZSTD_createDStream`, `ZSTD_initDStream`, `ZSTD_decompressStream`, `ZSTD_DStreamOutSize`, and `ZSTD_freeDStream`. `testFrameDecoding()` uses `ZSTD_decompressBound` and `ZSTD_findFrameCompressedSize`.

Control flow: `main()` runs simple one-shot decode, streaming decode, and frame-size traversal in order. The simple API allocates the exact expected size and compares full output. The streaming API decodes into chunks, reinitializing the stream when a frame ends, and compares each produced range against `EXPECTED`. Frame decoding walks all concatenated frames by repeatedly finding compressed frame sizes until no bytes remain.

State and persistence: Uses static `COMPRESSED` and `EXPECTED` string constants; heap allocations are per test and freed. No files are read or written.

Dependencies and integration points: Requires libzstd built with legacy decompression support. Includes `ZSTD_STATIC_LINKING_ONLY` for `ZSTD_decompressBound` and `zstd_errors.h` for legacy-specific error comparison.

Risks: Without legacy support, the simple API reports prefix unknown and fails. `strlen(EXPECTED)` assumes no embedded NULs in expected text. Streaming comparison depends on correct `outputPos` tracking across concatenated frames.

Test signals: Prints `Simple API OK`, `Streaming API OK`, `Frame Decoding OK`, and `OK`; exits nonzero on any decode, size, frame-bound, or content mismatch.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/legacy.c -->
