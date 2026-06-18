# sources/distributed-fs/ceph-client/tools/include/linux/bitmap.h

## Purpose

This header provides kernel-style bitmap declarations, allocation helpers, and inline operations for tools code.

## APIs, State, and Dependencies

It defines `DECLARE_BITMAP`, first/last word masks, `bitmap_size`, `bitmap_zero`, `bitmap_fill`, `bitmap_copy`, `bitmap_empty`, `bitmap_full`, `bitmap_weight`, logical operations, allocation/free helpers, `bitmap_scnprintf`, `bitmap_set`, `bitmap_clear`, and `bitmap_xor`. Larger operations delegate to external `__bitmap_*` functions. Small constant bit counts use optimized single-word operations. It depends on bitsperlong, align, bitops, find, stdlib, string, and kernel helpers.

## Risks and Test Signals

The header mixes inline optimized paths and external implementations, so behavior must match for small and large bitmaps. Endianness controls memory comparison alignment. Tests should cover zero/fill/copy, set/clear ranges, logical ops, subset/intersection/equality, allocation sizes, and boundary bit counts around `BITS_PER_LONG`.
