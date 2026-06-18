# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.h

## Purpose
This header defines XFS per-allocation-group in-core structures, reservation data, opstate helpers, perag reference/iteration helpers, AG geometry validation helpers, and prototypes for AG lifecycle/grow/shrink functions.

## Important Types and APIs
- `struct xfs_ag_resv` tracks original reserved, currently reserved, and requested blocks for a per-AG reservation.
- `struct xfs_perag` embeds `struct xfs_group` and caches AGF/AGI counters, btree levels, free/inode counts, metadata reservations, inode allocation search hints, inode cache state, and blockgc work.
- Opstate bits include `AGF_INIT`, `AGI_INIT`, `PREFERS_METADATA`, `ALLOWS_INODES`, and `AGFL_NEEDS_RESET`, with generated inline testers.
- Reference helpers distinguish passive refs (`xfs_perag_get/hold/put`) from active refs (`xfs_perag_grab/rele`) and wrap generic `xfs_group` operations.
- Iteration helpers include `xfs_perag_next_range`, `xfs_perag_next_from`, `xfs_perag_next`, and wrap-around macros for allocation scans.
- Geometry helpers verify AG block extents, AG inode numbers, log containment, and convert AG block/inode numbers to fsblock, disk address, or inode number.
- `struct aghdr_init_data` carries state for new AG header initialization.

## Control Flow and Usage
Most functions are inline wrappers used throughout XFS allocator, inode allocation, scrub, and growfs paths. Allocation scans use wrap iterators to grab each AG in an order that respects locality and deadlock constraints. Verifiers and allocation code use cached perag geometry to reject invalid block/inode numbers without rereading disk headers.

## State and Persistence Behavior
`xfs_perag` is in-core only, but mirrors persistent AGF/AGI values such as free blocks, freelist count, btree levels, and inode counts. Reservation fields affect global free-block accounting through allocator code, though the reservation itself is a virtual in-core accounting construct rather than an on-disk allocation.

## Dependencies and Integration Points
This header sits between generic group management (`xfs_group.h`), allocator code, inode allocation, rmap/refcount btrees, mount geometry, online repair, inode cache, and background block garbage collection. Kernel-only fields are guarded by `__KERNEL__`.

## Risks and Edge Cases
Incorrect reference type use can race unmount or AG teardown. Stale cached AGF/AGI counters can lead to allocator misbehavior, so initialization opstate bits matter. AG inode validation must account for static metadata and short last AGs. Wrap iteration must release the current AG before grabbing the next to avoid leaks and stale refs.

## Test Signals
Compile tests should cover kernel and userspace libxfs includes. Runtime signals include AG iteration under grow/shrink, inode allocation range checks, short-last-AG geometry, blockgc cancellation during perag free, online repair alternate btree heights, and lock/reference debugging for perag get/grab/put/rele paths.
