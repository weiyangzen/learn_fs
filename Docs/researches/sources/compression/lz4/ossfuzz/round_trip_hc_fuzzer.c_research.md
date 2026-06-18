# sources/compression/lz4/ossfuzz/round_trip_hc_fuzzer.c

## Purpose
This harness validates high-compression LZ4 block round trips for fuzzed input and fuzzed HC compression levels.

## Important APIs, Types, And Functions
It uses `FUZZ_dataProducer_range32()` for the level, `LZ4_compressBound()`, `LZ4_compress_HC()`, `LZ4_decompress_safe()`, and HC level constants.

## Control Flow
The producer consumes a level from `[LZ4HC_CLEVEL_MIN, LZ4HC_CLEVEL_MAX]` and leaves the remaining byte count as input size. Destination capacity is the standard compression bound, so HC compression is expected to succeed. The decoded result must match exactly.

## State, Persistence, And Dependencies
All state is local: producer, compressed buffer, and round-trip buffer. The HC compressor uses its own internal temporary state through `LZ4_compress_HC()`.

## Integration Points
This is the strict success-path target for `lz4hc.c` block compression and complements `compress_hc_fuzzer.c`, which stresses undersized outputs and `destSize`.

## Risks
`data` is not advanced after producer consumption, so the payload includes leading control bytes with reduced length. Zero-size buffers depend on malloc behavior. The target does not exercise streaming HC dictionaries.

## Test Signals
Signals include HC compression failure with compression-bound capacity, decompression failure, corruption, and level-specific regressions between hash-chain and optimal-parser modes.
