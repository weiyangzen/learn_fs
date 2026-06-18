# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/array.rs

Purpose: provides the small-allocation-count implementation of Binder mmap range allocation. It tracks only allocated or reserved ranges in a sorted array and is used until the descriptor count reaches `TREE_THRESHOLD`.

Important APIs/types/functions: `ArrayRangeAllocator<T>` stores sorted `Range<T>` descriptors, total size, and remaining async/oneway space. `FindEmptyRes` records insertion index and offset. Main methods are `new`, `is_full`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `debug_print`, and `low_oneway_space`. `EmptyArrayAlloc` preallocates the descriptor vector.

Control flow: `reserve_new` checks async-space quota for oneway transactions, searches for a gap by appending after the last range or scanning preceding gaps, inserts a reserved descriptor within capacity, and reports oneway spam suspicion when free async space is low and the caller owns many buffers. `reservation_commit` changes a reserved descriptor into allocated and stores optional metadata. `reserve_existing` changes allocated back to reserved while returning size, debug id, and metadata. `reservation_abort` removes a still-reserved descriptor and computes which interior or boundary pages are no longer covered by neighboring ranges.

State and persistence: state is in the process `RangeAllocator` inside `ProcessInner.mapping`. Descriptors are volatile transaction-buffer state. `free_oneway_space` starts at half the mmap size and is decremented only for oneway reservations.

Dependencies and integration points: used by `range_alloc/mod.rs`, which supplies preallocation and switches to the tree allocator when full. It relies on `DescriptorState`, `FreedRange`, `Range`, `Pid`, page constants, `KVec`, and seq-file debugging.

Risks: linear scans are intentional for small counts but depend on sorted insertion. Page-free calculations around unaligned boundaries must remain synchronized with `ShrinkablePageRange::stop_using_range`; off-by-one errors could mark a page reclaimable while another allocation still overlaps it. `insert_within_capacity(...).unwrap()` is safe only because callers preallocate exactly the threshold capacity.

Test signals: allocate/free gaps at beginning, middle, and end; unaligned buffers sharing pages; transition from reserved to allocated and back; oneway quota exhaustion; spam detection after many same-pid async buffers; and migration to tree when `is_full` becomes true.
