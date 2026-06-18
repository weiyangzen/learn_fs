<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h

## Purpose
Defines a DMA fence container that represents completion of an array of fences, either all fences or any fence depending on initialization.

## Important APIs, Types, And Functions
Types are `struct dma_fence_array_cb` and `struct dma_fence_array`. Helpers include `to_dma_fence_array()`, `dma_fence_array_for_each`, `dma_fence_array_alloc()`, `dma_fence_array_init()`, `dma_fence_array_create()`, `dma_fence_match_context()`, `dma_fence_array_first()`, and `dma_fence_array_next()`.

## Control Flow
Callers allocate/create an array fence with child fence pointers, a context, seqno, and `signal_on_any` policy. The array attaches callbacks to children and signals the base fence when the pending count reaches the selected condition. Iterators either walk children or treat a non-array head as a single fence.

## State And Persistence
State includes the base fence, spinlock, child count, atomic pending count, child fence array, IRQ work, and per-child callbacks. Lifetime is refcounted through the base fence and child references.

## Dependencies And Integration Points
Depends on `dma-fence.h` and IRQ work. Used by reservation objects, DRM schedulers, and sync-file style aggregation.

## Risks And Edge Cases
Child fence references and callback removal must be balanced. Empty arrays, already signaled children, and signal-on-any semantics need careful handling. Recursive container nesting is avoided by deeper unwrap helpers.

## Test Signals
Tests should cover all-children and any-child signal modes, already signaled children, mixed errors, context matching, iterator behavior for array and non-array fences, callback removal, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h -->
