# sources/compression/lz4/ossfuzz/compress_hc_fuzzer.c

## Purpose
This target fuzzes high-compression block APIs with variable compression levels and constrained destination sizes. It covers both normal HC compression and HC destination-size mode.

## Important APIs, Types, And Functions
The harness uses `LZ4_compress_HC()`, `LZ4_compress_HC_destSize()`, `LZ4_sizeofStateHC()`, `LZ4_decompress_safe()`, `LZ4HC_CLEVEL_MIN`, `LZ4HC_CLEVEL_MAX`, and producer helpers for capacity and level selection.

## Control Flow
Two producer values select destination capacity and HC level. Capacity is limited to `[0, size]`, increasing failure pressure. `LZ4_compress_HC()` may fail; successful output must decode to the effective input. When capacity is positive, the harness allocates an HC state, calls `LZ4_compress_HC_destSize()`, asserts success, and checks that the decoded bytes equal the consumed prefix.

## State, Persistence, And Dependencies
The only retained state is the temporary HC workspace allocated with `malloc(LZ4_sizeofStateHC())`. The library initializes that workspace inside the dest-size call. All buffers are freed before return.

## Integration Points
This target directly covers `lz4hc.c` block and fill-output paths. It complements `round_trip_hc_fuzzer.c`, which uses full compression bounds and requires normal HC compression success.

## Risks
`malloc(0)` behavior can affect assertions for zero-size buffers. The harness narrows `size_t` to `int` for library calls. Since capacity is capped at input size rather than `LZ4_compressBound()`, most incompressible cases stress failure cleanup and dirty-state handling.

## Test Signals
Useful signals are crashes, successful HC output that fails decompression, dest-size success with wrong consumed length, and state-size or alignment regressions.
