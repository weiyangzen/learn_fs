# sources/distributed-fs/ceph-client/lib/find_bit.c

## Purpose
Provides generic fallback implementations for the kernel `find_*_bit` bitmap search family when an architecture has not supplied optimized versions. It also implements nth-bit, clump, little-endian-on-big-endian, and random-set-bit helpers.

## Important APIs, Types, and Functions
Exported functions include `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_andnot_bit()`, `_find_first_and_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `__find_nth_bit()`, `__find_nth_and_bit()`, `__find_nth_and_andnot_bit()`, `_find_next_and_bit()`, `_find_next_andnot_bit()`, `_find_next_or_bit()`, `_find_next_zero_bit()`, `_find_last_bit()`, `find_next_clump8()`, endian-specific `_find_*_bit_le()` variants on big-endian builds, and `find_random_bit()`.

The core logic is in macros `FIND_FIRST_BIT`, `FIND_NEXT_BIT`, and `FIND_NTH_BIT`, parameterized by fetch and word-munging expressions.

## Control Flow
First/next search routines scan word by word, mask off bits before the requested start, and use `__ffs()` to return the first matching bit or `size` when none exists. Nth-bit routines count set bits with `hweight_long()` until the requested ordinal is in the current word, then use `fns()`. Last-bit search starts from the final masked word and scans backward with `__fls()`. `find_random_bit()` computes bitmap weight and selects a random ordinal for multi-bit maps.

## State and Persistence
The file is stateless and operates on caller-provided bitmaps. It does not modify input bitmaps except for outputting an 8-bit clump through `find_next_clump8()`.

## Dependencies and Integration Points
Depends on `linux/bitops.h`, `linux/bitmap.h`, endian byte swapping, random helpers, and exported symbols used throughout scheduler, memory-management, filesystem, and driver code. Architecture headers may define optimized variants, in which case guarded fallback functions are not compiled.

## Risks
Boundary handling around `size`, `start`, partial final words, and big-endian little-endian conversions is critical. `find_random_bit()` is O(weight/word scan) and not suitable for cryptographic randomness. Generic fallbacks affect many subsystems on architectures without overrides, so regressions have wide blast radius.

## Test Signals
Boot success is broad coverage, but targeted bitmap tests should verify empty/full maps, one-bit maps, partial final words, all boolean combinations, nth-bit out of range, clump alignment, big-endian LE variants, and random selection constrained to set bits.
