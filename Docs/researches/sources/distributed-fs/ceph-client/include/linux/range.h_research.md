# sources/distributed-fs/ceph-client/include/linux/range.h

Purpose: defines a simple inclusive `u64` range helper type and operations for adding, merging, subtracting, sorting, and cleaning range arrays.

Important APIs and types: `struct range` has inclusive `start` and `end`. Inline helpers include `range_len()`, `range_contains()`, `range_overlaps()`, and `DEFINE_RANGE()`. Extern functions include `add_range()`, `add_range_with_merge()`, `subtract_range()`, `clean_sort_range()`, and `sort_range()`.

Control flow: callers maintain a fixed-size array of ranges, add or merge intervals, subtract excluded intervals, then sort and clean overlapping or invalid entries before consuming the result.

State and persistence: state is caller-owned in-memory range arrays. There is no persistence.

Dependencies and integration points: depends only on Linux types and is commonly useful for memory/resource maps, firmware reservations, and architecture setup code.

Risks and test signals: risks include inclusive-end overflow in `range_len()`, invalid `start > end` ranges, array capacity truncation, merge/subtract boundary mistakes, and unsorted input assumptions. Test adjacent/overlapping/disjoint intervals, zero-length single-element ranges, full `u64` boundaries, subtraction splitting, and capacity exhaustion.
