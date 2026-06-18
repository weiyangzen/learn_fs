# sources/compression/zstd/examples/streaming_memory_usage.c

Purpose: reports and validates estimated versus actual memory usage for zstd streaming compression/decompression across compression levels, optionally with a caller-supplied window log.

Important functions/APIs: `readU32FromChar`, `main`, `ZSTD_createCCtxParams`, `ZSTD_CCtxParams_setParameter`, `ZSTD_estimateCStreamSize_usingCCtxParams`, `ZSTD_sizeof_CStream`, `ZSTD_sizeof_DStream`, `ZSTD_estimateDStreamSize_fromFrame`, `ZSTD_compressStream`, `ZSTD_endStream`, and `ZSTD_decompressStream`.

Control flow: parse optional window-log-like numeric value with K/M suffix support. For each level up to `MAX_TESTED_LEVEL`, set compression level and window log in params, create CCtx and apply params, compress a tiny in-memory payload without pledged size, finish the frame, create DCtx with optional max window log, decompress the frame, compare actual context sizes to estimates, print KB values, then free contexts. If a window log was supplied, only one level is tested.

State and persistence: all data is in fixed stack buffers and heap zstd contexts; no files are touched.

Dependencies/integration: static-linking-only zstd visibility for size estimation APIs, `common.h` checks, public streaming APIs.

Risks: `readU32FromChar` can overflow silently and does little validation after numeric suffix parsing. The sample payload is tiny, so it exercises maximum allocation behavior by API choice rather than realistic throughput. Output is informational and can vary by build options.

Test signals: examples Makefile invokes it; run with no argument and with explicit window log values, verify actual sizes do not exceed estimates, and test unusual suffix strings.
