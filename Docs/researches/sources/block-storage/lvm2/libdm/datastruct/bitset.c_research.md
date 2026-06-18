# File Research: sources/block-storage/lvm2/libdm/datastruct/bitset.c

## Purpose
Implements libdm bitset allocation, boolean operations, bit iteration, and parsing of textual CPU/list-style ranges into bitsets.

## Main Responsibilities
- Allocate bitsets either from a dm memory pool or heap.
- Store bit count in `bs[0]`; following words store bit values.
- Compare, intersect, and union bitsets.
- Iterate set bits forward or backward.
- Parse comma/range list syntax into a bitset.

## Key Functions
- `dm_bitset_create()` allocates enough integer words for `num_bits` plus metadata.
- `dm_bitset_destroy()` frees heap-allocated bitsets.
- `dm_bitset_equal()`, `dm_bit_and()`, and `dm_bit_union()` operate wordwise.
- `dm_bit_get_next()` and `dm_bit_get_prev()` scan set bits using `ffs()` and `clz()`.
- `dm_bitset_parse_list()` parses strings like `1,3-5`, determines required bit count on a first pass, then allocates and fills the mask on a second pass.
- `dm_bitset_parse_list_v1_02_129()` preserves ABI compatibility for older callers without `min_num_bits`.

## Edge Cases and Invariants
- Whitespace is allowed around values but not between digits.
- Empty fields are skipped.
- Descending ranges and dangling `-` are rejected.
- On parse failure, allocated masks are freed from the correct allocator.
- `min_num_bits` can force a larger empty tail even when parsed values are smaller.
