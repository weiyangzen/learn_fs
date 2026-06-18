# sources/compression/lz4/ossfuzz/round_trip_frame_fuzzer.c

## Purpose
This harness requires LZ4 frame compression to succeed with ample output capacity, then verifies exact decompression back to the input.

## Important APIs, Types, And Functions
It uses `FUZZ_dataProducer_preferences()`, `LZ4F_compressFrameBound()`, `LZ4_compressBound()`, `LZ4F_compressFrame()`, `LZ4F_isError()`, `FUZZ_decompressFrame()`, and `memcmp()`.

## Control Flow
The producer derives frame preferences and the remaining size. The harness allocates a destination using a conservative frame bound over `LZ4_compressBound(size)` and a round-trip buffer for the remaining bytes. Compression is asserted successful; decompression size and content must match.

## State, Persistence, And Dependencies
All state is local heap memory plus the producer. The strict frame decompression context is created inside `FUZZ_decompressFrame()`.

## Integration Points
This target validates the normal success path for frame compression under fuzzed preferences. It complements `compress_frame_fuzzer.c`, which intentionally allows too-small outputs.

## Risks
The original `data` pointer is not advanced after producer consumption, only `size` is reduced, so the tested payload starts at the beginning of the fuzz buffer with a shorter length. The destination bound is larger than necessary, which is safe but may reduce pressure on boundary conditions.

## Test Signals
Signals are frame-compression errors despite sufficient space, strict decompression failures, checksum regressions, and content corruption across preference combinations.
