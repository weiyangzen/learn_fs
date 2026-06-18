# sources/compression/zstd/tests/fuzz/simple_round_trip.c

## Purpose

`simple_round_trip.c` validates zstd one-shot compression/decompression correctness over randomized compression parameters. It also checks compression determinism for identical parameters and tests in-place decompression margin behavior.

## Important APIs And Functions

`getDecompressionMargin()` compares `ZSTD_decompressionMargin()` with `ZSTD_DECOMPRESSION_MARGIN()` when small-block targeting is not active. `roundTripTest()` drives compression, determinism hashing with `XXH64()`, optional decoder max-block-size enforcement, normal decompression, and margin-based in-place decompression.

Important zstd APIs include `ZSTD_compress2()`, `ZSTD_compressCCtx()`, `ZSTD_decompressDCtx()`, `ZSTD_getFrameHeader()`, `ZSTD_CCtx_getParameter()`, `ZSTD_DCtx_setParameter()`, `ZSTD_decompressionMargin()`, and `ZSTD_DECOMPRESSION_MARGIN()`.

## Control Flow

The input is split into parameter and source bytes. The target allocates an output buffer sized to source size and a compressed buffer of `ZSTD_compressBound(size)` minus zero or one byte. It creates static compression/decompression contexts and calls `roundTripTest()`.

`roundTripTest()` randomly chooses between full random parameter compression via `FUZZ_setRandomParameters()` and simple compression-level compression. In both branches it compresses twice with the same settings and asserts identical compressed size and XXH64 hash. It then optionally sets the decoder max block size, performs normal decompression with exact byte comparison, computes decompression margin, places the compressed frame at the end of a shared buffer, and verifies in-place-style decompression into the front of that buffer.

## State And Persistence

`cctx` and `dctx` are static and persist under `STATEFUL_FUZZING`; otherwise they are freed per input. All source/output/compressed buffers are per test case. Optional third-party sequence producer state is per case.

## Dependencies And Integration Points

The target depends on zstd static APIs, random parameter helpers, xxhash via `fuzz_helpers.h`, and optional sequence producer registration. It is one of the broadest coverage targets for normal frame compression, decompression, frame headers, deterministic output, and decompression-margin contracts.

## Risks And Edge Cases

Edges include empty input, one-byte-shrunken compression buffer, random max block sizes, target compressed block size, long-distance match settings, checksum/content-size/dict-ID flags, and in-place layout where input overlaps the output allocation. The superblock expansion assertion is intentionally disabled because target-block mode can currently expand too much in the worst case.

## Test Signals

High-value signals are nondeterministic compressed output for identical parameters, decompressed-size mismatch, byte corruption, invalid decompression margin, or max-block-size decoder failures. Corpus inputs should exercise both compression branches and the optional random decoder max-block setting.
