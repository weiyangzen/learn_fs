# sources/compression/zstd/tests/fuzz/simple_compress.c

## Purpose

`simple_compress.c` fuzzes the simple one-shot compression API with random input, compression level, and output capacity. It ensures `ZSTD_compressCCtx()` either succeeds or fails only with the expected destination-too-small error.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. It uses `ZSTD_createCCtx()`, `ZSTD_compressBound()`, `ZSTD_compressCCtx()`, `ZSTD_isError()`, and `ZSTD_getErrorCode()`. Compression levels are selected between `kMinClevel` and `kMaxClevel` from `zstd_helpers.c`.

Optional sequence-producer setup/teardown macros wrap the test, allowing this simple API harness to also exercise registered third-party sequence producers through shared helper configuration.

## Control Flow

The producer reserves prefix bytes, computes the maximum compressed bound for the remaining source, picks an output buffer size from zero to the bound, and chooses a compression level. A static compression context is created if needed. The compression call is performed once; if it returns an error, the error code must be `ZSTD_error_dstSize_tooSmall`.

## State And Persistence

`cctx` is static and persists under `STATEFUL_FUZZING`; otherwise it is freed after each input. The result buffer and data producer are per invocation. Sequence producer state is per test case when enabled.

## Dependencies And Integration Points

The file depends on public zstd compression APIs, zstd error codes, shared fuzz helpers, and optional third-party sequence producer support. It is a broad smoke target for the simplest compression entry point.

## Risks And Edge Cases

The main edge is zero or undersized destination capacity. Since arbitrary output size is allowed, unexpected error codes indicate API contract regression. The target does not validate successful compressed output, so corruption detection is left to round-trip fuzzers.

## Test Signals

Success means no crash and no compression error except `dstSize_tooSmall`. Corpus entries should include empty input, small output buffers, and high/negative compression levels.
