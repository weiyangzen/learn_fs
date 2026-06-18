<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h

Purpose: defines the range-fence data structures and public interval-tree API.

Important types and APIs: `struct xe_range_fence_ops` supplies an optional `free()` callback; `struct xe_range_fence` stores RB node, inclusive start/last, subtree metadata, fence reference, tree pointer, DMA fence callback, pending-free list node, and ops; `struct xe_range_fence_tree` stores root and pending list. Public functions initialize/finalize trees, insert fences, and iterate overlapping ranges. `xe_range_fence_kfree_ops` frees nodes with `kfree()`.

Risks and test signals: the header documents inclusive `last` semantics, while the insert argument is named `end` in the prototype. Callers should be tested for off-by-one range handling and external locking discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h -->
