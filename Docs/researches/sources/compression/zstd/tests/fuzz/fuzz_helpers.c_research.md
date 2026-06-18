# sources/compression/zstd/tests/fuzz/fuzz_helpers.c

## Purpose
This helper implementation provides fuzz-specific utility functions shared across zstd fuzz targets.

## APIs and behavior
The implementation defines `FUZZ_malloc()`, `FUZZ_malloc_rand()`, and `FUZZ_memcmp()`. `FUZZ_malloc()` returns `NULL` for zero-size allocations and asserts successful allocation otherwise. `FUZZ_malloc_rand()` behaves similarly for nonzero sizes, but for zero-size requests it may return either `NULL` or a fuzz-selected junk pointer to stress APIs that must ignore zero-capacity buffers. `FUZZ_memcmp()` treats zero-size comparisons as equal before delegating to `memcmp()`.

## State, dependencies, risks, and test signals
There is no persistent state. Dependencies are standard allocation/memory behavior, assertions from the companion header, and `FUZZ_dataProducer_t` for randomized zero-size pointers. The main risk is global blast radius: allocation or comparison semantics affect many fuzz targets. Test signals include immediate assertion on unexpected allocation failure and round-trip targets aborting/asserting when `FUZZ_memcmp()` reports corruption.
