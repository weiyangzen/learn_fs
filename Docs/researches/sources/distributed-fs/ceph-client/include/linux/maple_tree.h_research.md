<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple_tree.h -->
# sources/distributed-fs/ceph-client/include/linux/maple_tree.h

## Purpose
This header defines the Linux Maple Tree API and internal layout: an RCU-aware adaptive range tree used for efficient index-to-pointer and range storage, including allocation-range gap tracking.

## Important APIs, types, and functions
Important node structures include `struct maple_range_64`, `struct maple_arange_64`, `struct maple_node`, `struct maple_copy`, and `struct maple_metadata`. Public tree state is `struct maple_tree`; advanced iteration/write state is `struct ma_state` plus `struct ma_wr_state`. Initialization macros include `MTREE_INIT`, `MTREE_INIT_EXT`, `DEFINE_MTREE`, `MA_STATE`, `MA_WR_STATE`, and `MA_TOPIARY`. Public operations include `mtree_load`, `mtree_insert`, `mtree_insert_range`, `mtree_alloc_range`, `mtree_alloc_cyclic`, `mtree_alloc_rrange`, `mtree_store_range`, `mtree_store`, `mtree_erase`, `mtree_dup`, `mtree_destroy`, `mas_walk`, `mas_store`, `mas_erase`, `mas_store_gfp`, `mas_store_prealloc`, `mas_find`, `mas_find_range`, reverse/find-next helpers, `mas_empty_area`, and `mt_find`/`mt_prev`/`mt_next` iterators.

## Control flow
Simple users initialize a tree, lock if required, and call `mtree_*` helpers for lookup, insertion, range store, allocation, or erase. Advanced users create an `ma_state`, walk or search the tree, optionally preallocate nodes, store or erase, and reset/pause the state when locks are dropped. RCU readers rely on encoded node pointers, immutable node type after insertion, and removed-node parent self-pointers to detect stale slots. Allocation-range trees track largest gaps to accelerate empty-area search.

## State and persistence
The persistent in-memory state is `ma_flags`, encoded height, optional RCU mode, lock mode, and `ma_root`. Nodes are 256-byte aligned and encode root/node type/slot information in low pointer bits. `ma_state` carries transient traversal position, range bounds, cached node, allocation staging, depth, offset, and store classification.

## Dependencies and integration points
It depends on kernel, RCU, spinlock, lockdep, slab sheaf allocation, and debug infrastructure. Integration points include memory-management VMA storage and any subsystem needing sparse ranges with RCU-friendly lookup.

## Risks and test signals
Risks are pointer-tag encoding errors, invalid storage of reserved low-bit patterns, stale `ma_state` reuse after unlocking, RCU mode transitions with external locks, gap metadata corruption, height overflow, and allocation preflight bugs. Test dense and sparse ranges, storing entries at index zero with all low-bit patterns, splitting/rebalancing, reverse searches, empty-area allocation, cyclic allocation wrapping, debug validation, RCU readers during mutation, and external-lock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple_tree.h -->
