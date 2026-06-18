# sources/compression/zstd/tests/fuzz/simple_decompress.c

## Purpose

`simple_decompress.c` fuzzes one-shot zstd decompression on arbitrary input and random output capacity. It is primarily a crash-resistance target, with an additional consistency check for successful decompressions.

## Important APIs And Functions

The entry point uses `ZSTD_createDCtx()`, `ZSTD_decompressDCtx()`, `ZSTD_findDecompressedSize()`, and zstd content-size sentinel values. It uses `FUZZ_dataProducer` to select an output buffer size up to `10 * size`.

## Control Flow

The fuzzer reserves parameter bytes, creates or reuses a decompression context, allocates an output buffer, and calls `ZSTD_decompressDCtx()` once. If decompression succeeds, it calls `ZSTD_findDecompressedSize()` on the same input and asserts that the result is not `ZSTD_CONTENTSIZE_ERROR` and is either unknown or exactly equal to the returned decompressed size.

## State And Persistence

`dctx` is static and persists only under `STATEFUL_FUZZING`; otherwise it is freed per input. The output buffer and producer are per invocation.

## Dependencies And Integration Points

This target uses zstd static-linking-only mode and public decompression/content-size helpers. It complements `zstd_frame_info.c`, which fuzzes metadata helpers without decompressing.

## Risks And Edge Cases

Important edges include empty input, valid frames with unknown content size, concatenated frames, truncated frames, output buffer size zero, and arbitrary non-frame data. The test intentionally accepts decompression errors but requires successful returns to agree with frame-size discovery.

## Test Signals

Signals include crashes, sanitizer findings, successful decompressions with content-size errors, or mismatches between known content size and returned decompressed size.
