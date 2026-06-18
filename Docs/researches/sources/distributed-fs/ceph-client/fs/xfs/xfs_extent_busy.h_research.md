# sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.h

## Purpose
`xfs_extent_busy.h` defines the busy extent data structures and allocator-facing API used to protect recently freed blocks from unsafe reuse.

## Important APIs, types, and functions
`struct xfs_extent_busy` is the rb-tree/list node for a busy range, with group pointer, AG-relative block, length, and flags `XFS_EXTENT_BUSY_DISCARDED` and `XFS_EXTENT_BUSY_SKIP_DISCARD`. `struct xfs_busy_extents` groups related extents through discard completion. The header declares insertion, clearing, search, reuse, trim, flush, wait, list-empty, tree allocation, and list sort helpers.

## Control flow
Transactions append busy entries through `xfs_extent_busy_insert`; CIL or discard completion clears lists; allocation code probes, trims, flushes, or reuses ranges before handing blocks back out. `xfs_extent_busy_sort` groups list entries by group and block to let clear operations process them efficiently.

## State and persistence
The declared objects represent in-memory transaction and discard state only. The `owner` field of `struct xfs_busy_extents` defines who is freed after endio-style processing.

## Dependencies and integration points
It forward-declares XFS mount, group, and transaction types and uses Linux rbtrees, lists, work structs, and list sorting. `xfs_group_has_extent_busy` encodes the integration rule that zoned realtime groups do not need normal busy extent tracking.

## Risks and test signals
Risks include incorrect group type decisions, caller misuse of busy lists after transaction attachment, and missed discard-skip semantics. Test signals are allocation/freeing tests on data AGs, non-zoned rtgroups, zoned rtgroups, discard-enabled mounts, and low-space retry paths.
