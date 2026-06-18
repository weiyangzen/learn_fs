# sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.h

## Purpose
`lcnalloc.h` declares the NTFS cluster allocation/deallocation interface and documents the locking contract for callers. It exposes allocation zones, the allocator entry point, the lower-level free routine, and convenience wrappers for freeing clusters from inode runlists or standalone runlists.

## Important APIs, Types, and Functions
The zone enum defines `MFT_ZONE` and `DATA_ZONE`, with `FIRST_ZONE` and `LAST_ZONE` aliases for validation. `ntfs_cluster_alloc()` allocates clusters and returns a runlist. `__ntfs_cluster_free()` is the full free implementation, including rollback mode. `ntfs_cluster_free()` is the normal inline wrapper with `is_rollback=false`. `ntfs_cluster_free_from_rl_nolock()` and `ntfs_cluster_free_from_rl()` free all concrete runs in a supplied runlist, with the latter taking and releasing the volume LCN bitmap lock.

## Control Flow and State
The header captures expected caller flow: hold the inode runlist lock for cluster-free operations, call allocation with the volume bitmap unlocked, and allow the implementation to take `vol->lcnbmp_lock`. For `ntfs_cluster_free_from_rl()`, callers must already stabilize the runlist while the wrapper handles bitmap locking and NOFS context.

## State and Persistence Behavior
The functions declared here mutate the persistent `$Bitmap` allocation map and volume free-space accounting in `lcnalloc.c`. The header's comments are persistence-relevant because they specify that `ntfs_cluster_free()` does not modify the inode runlist; callers must later remove or mark freed runs so runlist state and on-disk allocation state do not diverge.

## Dependencies and Integration Points
It includes `linux/sched/mm.h` for NOFS memory-allocation context and `attrib.h` for NTFS volume, inode, runlist, and attribute-search types. It is used by attribute expansion/truncation, delayed allocation, rollback, and metadata cleanup paths that need cluster ownership changes.

## Risks
The risk is misuse of locking or post-free runlist handling. Calling the free API without a write-locked runlist can race runlist mapping or truncation. Assuming the free API edits the runlist would leave stale mappings to freed clusters. Supplying an invalid `ctx` can leave `ctx->mrec` as an error pointer per the warning in the contract.

## Test Signals
Compile coverage should verify API signatures. Runtime signals include truncation, hole punching/sparse conversion if supported, allocation rollback, cluster free with and without an existing attribute search context, and lockdep checks for runlist and bitmap lock ordering.
