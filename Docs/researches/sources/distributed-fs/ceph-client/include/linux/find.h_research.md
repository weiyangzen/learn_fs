# sources/distributed-fs/ceph-client/include/linux/find.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/find.h` provides bitmap bit-search helpers and iteration macros used throughout the kernel. It is intentionally included through `linux/bitmap.h`. The source was read as a complete 695-line file for this report.

## Important APIs, Types, and Functions

Important functions/macros include `_find_next_bit`, `_find_next_and_bit`, `_find_next_andnot_bit`, `_find_next_or_bit`, `_find_next_zero_bit`, `_find_first_bit`, `__find_nth_bit`, `__find_nth_and_bit`, `__find_nth_and_andnot_bit`, `_find_first_and_bit`, `_find_first_andnot_bit`, `_find_first_and_and_bit`, `_find_first_zero_bit`, `_find_last_bit`, endian-specific `_find_*_le`, `find_random_bit`, inline `find_next_bit`, `find_next_and_bit`, `find_next_andnot_bit`, `find_next_or_bit`, `find_next_zero_bit`, `find_first_bit`, `find_nth_bit`, `find_nth_and_bit`, `find_first_andnot_bit`, `find_last_bit`, wrap helpers, `find_next_clump8`, and iteration macros such as `for_each_set_bit`, `for_each_clear_bit`, bitrange iterators, and clump iterators.

## Control Flow

Callers search bitmaps for set, clear, combined, excluded, or nth bits. For compile-time small bitmaps, inline paths mask a single word and use `__ffs`, `ffz`, `__fls`, or `fns`; larger cases call architecture/generic implementations. Wrap helpers search from an offset and wrap to the beginning. Iteration macros repeatedly call the find helpers and increment past found bits/ranges.

## State and Persistence Behavior

No state is owned by the header. It operates over caller-owned bitmap memory.

## Dependencies and Integration Points

It depends on bitops, endian definitions, and bitmap inclusion discipline. It is used by cpumasks, nodemasks, allocation bitmaps, fd bitmaps, page/block allocators, scheduler masks, and many driver resource maps.

## Risks and Edge Cases

Size and offset bounds are critical: helpers return `size` when not found. Small-constant masks must avoid invalid shifts. Big-endian little-endian bitmap helpers swab word values. Iteration macros assign inside loop conditions and require caller variables with appropriate unsigned types.

## Test Signals

lib/bitmap tests, bitops tests on 32-bit/64-bit and big/little-endian targets, randomized bitmap search comparisons, boundary tests for size 0/1/BITS_PER_LONG, and wrap/clump iteration tests.
