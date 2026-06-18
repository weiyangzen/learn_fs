<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c

Purpose: implements address-range conflict tracking backed by Linux interval trees and DMA fences. A range fence remains in the tree until its associated `dma_fence` signals, then cleanup removes it and frees storage.

Important APIs and control flow: `xe_range_fence_insert()` cleans pending signaled entries, ignores already-signaled fences, initializes the interval-tree node, gets the fence, registers `xe_range_fence_signal_notify()`, and inserts the node. The fence callback only adds the range fence to an `llist`, deferring removal/free until `__xe_range_fence_tree_cleanup()` runs in non-callback context. `xe_range_fence_tree_first()` and `_next()` wrap generated interval-tree iterators.

State and dependencies: `struct xe_range_fence_tree` owns a cached RB root and lockless list of pending frees. `xe_range_fence_tree_fini()` removes callbacks from all live fences and loops cleanup until empty.

Risks and test signals: callback/removal races are subtle; tests should cover insertion with pre-signaled fences, callback firing during fini, overlapping iterator queries, and custom `ops->free`. Callers must provide external synchronization around tree access because this file does not embed a lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c -->
