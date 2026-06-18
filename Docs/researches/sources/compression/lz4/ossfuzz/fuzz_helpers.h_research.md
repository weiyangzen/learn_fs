# sources/compression/lz4/ossfuzz/fuzz_helpers.h

## Purpose
`fuzz_helpers.h` provides always-on assertions, deterministic seed generation, and a tiny pseudo-random generator for the LZ4 fuzz harnesses.

## Important APIs, Types, And Functions
Key macros are `FUZZ_ASSERT_MSG`, `FUZZ_ASSERT`, `FUZZ_STATIC`, `MIN`, and `MAX`. Inline helpers are `FUZZ_seed()`, `FUZZ_rand()`, and `FUZZ_rand32()`. `FUZZ_seed()` hashes up to `FUZZ_RNG_SEED_SIZE` leading bytes with `XXH32` and advances the caller's input pointer and size.

## Control Flow
Assertions print file, line, failed expression, and message to stderr, then abort. `FUZZ_rand()` updates a 32-bit state with multiply/add/rotate and returns high bits. `FUZZ_rand32()` maps that value into an inclusive range.

## State, Persistence, And Dependencies
The helper stores no global state. PRNG state is caller-owned. It includes `fuzz.h`, `xxhash.h`, standard headers, and, when needed, `lz4.c` with `LZ4_COMMONDEFS_ONLY` to access shared LZ4 debug and memory definitions.

## Integration Points
All fuzz targets use these assertions and many use the RNG. `round_trip_stream_fuzzer.c` relies on `FUZZ_seed()` for deterministic stream slicing and dictionary choices.

## Risks
`FUZZ_rand32()` assumes `max >= min` and that `(max - min + 1)` does not wrap unexpectedly. The header defines generic `MIN` and `MAX`, which can collide with other headers. Including `lz4.c` internals from a header is convenient but sensitive to compile-unit macro ordering.

## Test Signals
Useful signals include deterministic output for fixed seeds, seed consumption behavior, assertion failure formatting, sanitizer builds, and compile tests with `LZ4_SRC_INCLUDED` already defined.
