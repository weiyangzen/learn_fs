# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_priv.h

## Purpose
`xfs_zone_priv.h` defines private zoned allocator structures shared by zone allocation, garbage collection, reservations, and stats code.

## Important APIs, types, and functions
It defines `struct xfs_open_zone`, `XFS_ZONE_USED_BUCKETS`, and `struct xfs_zone_info`. It declares `xfs_open_zone`, `xfs_zone_gc_reset_sync`, `xfs_zoned_need_gc`, `xfs_zoned_have_reclaimable`, `xfs_zone_gc_mount`, `xfs_zone_gc_unmount`, and `xfs_zoned_resv_wake_all`.

## Control flow
Open zones are tracked in a mount-level list, refcounted, and tied to realtime groups. `oz_allocated` advances when writeback reserves blocks; `oz_written` advances at write completion under the rmap inode lock. `xfs_zone_info` coordinates open-zone limits, free-zone counts, reservation waiters, GC thread, reset list, and reclaimable-zone buckets.

## State and persistence
All structures are in-memory. They mirror persistent/device state in rmap used counters and zone write pointers but are rebuilt at mount. RCU frees open zones after refs drop so cached inode pointers can be looked up safely.

## Dependencies and integration points
The header is private to zoned XFS implementation files and depends on list heads, atomics, wait queues, spinlocks, task structs, realtime groups, and write-life hints.

## Risks and test signals
Risks include incorrect lock ownership around `oz_written`, open-zone list count drift, reset-list races, bucket bitmap leaks, and cached pointer lifetime mistakes. Test signals include lockdep, RCU stress, mount/unmount under active writeback, GC with reservation waiters, and stats while zones transition.
