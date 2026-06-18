<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bitmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/bitmap.c

## Purpose
`bitmap.c` supplies userspace implementations of common Linux bitmap primitives for tools. It operates on arrays of `unsigned long` and mirrors kernel bitmap semantics for weights, set algebra, formatting, and bit range modification.

## Important APIs, types, and functions
Implemented functions include `__bitmap_weight()`, `__bitmap_or()`, `bitmap_scnprintf()`, `__bitmap_and()`, `__bitmap_equal()`, `__bitmap_intersects()`, `__bitmap_set()`, `__bitmap_clear()`, `__bitmap_andnot()`, `__bitmap_subset()`, and `__bitmap_xor()`. It relies on macros and helpers from `<linux/bitmap.h>` such as `BITS_PER_LONG`, `BITS_TO_LONGS`, `BITMAP_LAST_WORD_MASK`, `find_first_bit()`, `find_next_bit()`, `hweight_long()`, and `scnprintf()`.

## Control flow
Most operations loop over whole words and handle a final partial word with a mask. `bitmap_scnprintf()` walks set bits, coalesces contiguous ranges, and writes comma-separated `n` or `n-m` spans. Range set/clear calculates first/last word masks and updates full middle words with all-bits masks.

## State and persistence behavior
There is no global state. All state is in caller-provided bitmaps and output buffers. Mutating operations write directly to `dst` or `map`.

## Dependencies and integration points
This file is part of tools/lib compatibility code used by perf and other tools that include Linux bitmap APIs in userspace.

## Risks and edge cases
Callers must provide buffers sized for `BITS_TO_LONGS(bits)`. Formatting uses `size - ret` without clamping when output is truncated, so underflow risks depend on `scnprintf()` semantics. Range helpers do not validate `start + len` against the actual map allocation. Negative `len` values are not guarded.

## Test signals
Compare operations against kernel bitmap expectations for zero bits, exact word sizes, partial final words, overlapping source/destination, formatted sparse and contiguous ranges, and set/clear ranges crossing word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bitmap.c -->
