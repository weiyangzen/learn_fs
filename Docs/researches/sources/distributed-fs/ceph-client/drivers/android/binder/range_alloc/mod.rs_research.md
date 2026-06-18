# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/mod.rs

Purpose: defines the common Binder transaction-buffer range allocator API and switches between empty, small-array, and RBTree-backed implementations. It also carries descriptor state and metadata for reserved versus allocated buffers.

Important APIs/types/functions: `DescriptorState<T>` is either `Reserved(Reservation)` or `Allocated(Allocation<T>)`. `Reservation` stores debug id, oneway flag, and sender pid; `Allocation<T>` stores committed metadata. `FreedRange` describes page indices that became fully free. `RangeAllocator<T>` exposes `new`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `free_oneway_space`, `count_buffers`, and `debug_print`. `ReserveNewArgs`, `ReserveNew`, `ReserveNewSuccess`, and `ReserveNewNeedAlloc` implement lock-friendly preallocation.

Control flow: a new allocator starts as `Empty(size)`. First reservation asks the caller to allocate an `EmptyArrayAlloc`, then becomes `Array`. When the array is full, `reserve_new` asks for `FromArrayAllocs` and a tree reservation, converts the sorted array into `TreeRangeAllocator`, and retries. Tree reservations require the caller to provide `ReserveNewTreeAlloc` before the lock is held. Abort, commit, reserve-existing, and shutdown dispatch to the active implementation; an empty tree collapses back to `Empty`.

State and persistence: the allocator is stored per process mapping and tracks live Binder transaction buffers until committed/freeable or aborted. It persists only for the lifetime of the Binder mmap. Optional `T` metadata is stored in allocated descriptors and returned to callers when a userspace buffer is reused/freed.

Dependencies and integration points: consumed by `Process::buffer_alloc`, `buffer_get`, `buffer_raw_free`, `buffer_make_freeable`, and release cleanup. It depends on `array.rs`, `tree.rs`, `PAGE_SIZE`, `Pid`, and seq-file output.

Risks: the preallocation handshake must be followed exactly so no GFP allocations are needed while the process spinlock is held. Incorrect state transitions can leak metadata, double-free ranges, or free pages too early. The array-to-tree threshold is part of performance behavior and should be changed only with allocator tests.

Test signals: cover first allocation from empty, repeated `NeedAlloc` retry paths, array-to-tree conversion at eight descriptors, commit/reserve-existing/abort state errors, allocator collapse to empty, shutdown `take_for_each`, and preservation of `AllocationInfo` metadata.
