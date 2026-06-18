# sources/distributed-fs/ceph-client/kernel/range.c

## Purpose
`range.c` provides small helper routines for adding, merging, subtracting, cleaning, and sorting arrays of half-open `struct range` intervals.

## Important APIs, types, and functions
The public helpers are `add_range()`, `add_range_with_merge()`, `subtract_range()`, `clean_sort_range()`, and `sort_range()`. `cmp_range()` is the local comparator used by `sort()`. The file operates on caller-owned `struct range` arrays with fixed slot count `az`.

## Control flow
`add_range()` appends a non-empty `[start, end)` interval if there is a free slot. `add_range_with_merge()` scans existing non-empty ranges for overlap or adjacency according to the `common_start > common_end` test, folds matching entries into the new start/end, removes consumed slots with `memmove()`, then appends the merged range. `subtract_range()` walks all slots and handles full removal, trimming from the front, trimming from the back, or splitting into a spare slot. `clean_sort_range()` compacts non-empty ranges toward the front, zeroes vacated slots, counts active ranges, and sorts by start. `sort_range()` sorts an already compact range array.

## State and persistence behavior
All mutations are in-place in the supplied array. Empty slots are represented by `end == 0` with start also usually zeroed. There is no synchronization, allocation, or persistent global state.

## Dependencies and integration points
The file depends on `linux/range.h`, min/max helpers, `memmove()`, kernel sort, and printk for split-without-slot errors. It is suitable for boot or architecture memory/resource range construction where fixed arrays are common.

## Risks and invariants
Callers must provide correct array size and external synchronization. Subtract splitting can lose the right-side fragment if no empty slot exists, logging an error but preserving the left fragment. The interval convention is effectively half-open because empty ranges satisfy `start >= end`; overlap/merge behavior treats touching intervals as mergeable when `common_start == common_end`.

## Test signals
Tests should cover empty additions, full arrays, overlapping and touching merges, non-overlapping ranges, subtract full/left/right/middle split, split without spare slot, compaction with holes, and sorted order after cleanup.
