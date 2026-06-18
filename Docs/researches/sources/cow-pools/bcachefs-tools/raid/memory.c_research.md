# File Research: sources/cow-pools/bcachefs-tools/raid/memory.c

## Purpose
Aligned allocation and memory test/fill helpers for the RAID library.

## APIs
- `raid_malloc_align()`
- `raid_malloc()`
- `raid_malloc_vector_align()`
- `raid_malloc_vector()`
- `raid_mrand_vector()`
- `raid_mtest_vector()`

## Behavior
- Allocates extra memory and returns an aligned pointer while storing the original pointer in `freeptr`.
- Vector allocation creates a pointer array and a contiguous aligned backing region.
- Data-block pointers are reversed to match access patterns that often iterate from last data block downward.
- Random fill uses a simple C99/C11-style linear congruential generator.
- Memory test cycles through byte patterns and complements to detect RAM/data path issues.

## Dependencies
Uses `internal.h` and `memory.h`.
