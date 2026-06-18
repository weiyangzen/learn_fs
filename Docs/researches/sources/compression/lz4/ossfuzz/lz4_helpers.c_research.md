# sources/compression/lz4/ossfuzz/lz4_helpers.c

## Purpose
`lz4_helpers.c` implements shared LZ4-frame helper routines for fuzz targets: randomized frame preferences and a strict one-shot frame decompression validator.

## Important APIs, Types, And Functions
`FUZZ_randomFrameInfo()` generates `LZ4F_frameInfo_t` from a `FUZZ_rand32()` seed. `FUZZ_randomPreferences()` wraps that in `LZ4F_preferences_t` and chooses compression level, auto-flush, and decompression-speed preference. `FUZZ_decompressFrame()` creates a decompression context, calls `LZ4F_decompress()` with `stableDst=1`, asserts full success and full input consumption, frees the context, and returns regenerated size.

## Control Flow
Preference generation chooses values from valid enum ranges and normalizes a below-minimum block size to default. Decompression initializes options to zero, sets stable destination, performs a single decompress call, and aborts if the frame is incomplete, erroneous, or not fully consumed.

## State, Persistence, And Dependencies
All state is local to the call. `FUZZ_decompressFrame()` owns one temporary `LZ4F_dctx`. There is no persistent data or global state.

## Integration Points
Frame compression and round-trip fuzzers use this helper to verify successful frame outputs. The data-producer implementation mirrors much of the random-preference logic for producer-driven fuzzers.

## Risks
`FUZZ_decompressFrame()` assumes the whole frame can be decompressed in one call and that the destination is large enough; it is suitable for validation of known-good compressed frames, not arbitrary malformed input. It asserts context creation but does not inspect the return code from `LZ4F_createDecompressionContext()`.

## Test Signals
Round trips with each block mode, checksum flag, block size, HC level, and auto-flush setting validate these helpers. Negative tests should confirm malformed frames abort through assertions.
