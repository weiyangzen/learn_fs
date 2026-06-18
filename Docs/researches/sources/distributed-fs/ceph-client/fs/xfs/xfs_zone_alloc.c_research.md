# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.c

## Purpose
`xfs_zone_alloc.c` implements the zoned realtime allocator for XFS. It discovers and tracks realtime groups as zones, selects open zones for writeback, submits zone append or conventional writes, remaps completed writes into file data forks, accounts reclaimable space, and mounts/unmounts zoned allocator state.

## Important APIs, types, and functions
Public functions include `xfs_open_zone_put`, `xfs_zoned_have_reclaimable`, `xfs_zoned_end_io`, `xfs_zone_free_blocks`, `xfs_open_zone`, `xfs_zone_alloc_and_submit`, `xfs_zoned_wake_all`, `xfs_zone_rgbno_is_valid`, `xfs_mount_zones`, and `xfs_unmount_zones`. Important internal helpers handle open-zone initialization, reclaim buckets, zone selection, inode zone caching, write pointer discovery, open-zone limits, and mount-time validation.

## Control flow
Mount requires an RT device, rtgroups, rmapbt, `rextsize == 1`, and enough zones. It allocates `m_zone_info`, reports each block zone or derives conventional write pointers from rmap, marks empty zones free, restores partially written zones as open, buckets reclaimable full zones, clamps open-zone limits, adjusts writeback granularity, and starts GC. Writeback selects a cached or list-managed open zone by write-life hint and packing policy, reserves a range under `oz_alloc_lock`, splits ioends at allocation or zone-append boundaries, and submits bios. Completion calls `xfs_zoned_end_io`, which transactions the new mapping, frees overwritten extents or decrements refcounts, increments rmap used/written counters, and skips speculative GC writes if another writer won the race.

## State and persistence
Runtime state is `struct xfs_zone_info`, open-zone refs, per-inode cached `i_private` zone pointers, free-zone xarray marks, used-bucket bitmaps, reset lists, and free counters. Persistent accounting is stored in realtime rmap inode `i_used_blocks` and file bmaps. Device write pointers persist on zoned media; conventional zones approximate them from rmap after mount.

## Dependencies and integration points
The file integrates with iomap writeback, realtime groups, rmap btrees, bmap and refcount code, free counters, GC, block zone APIs, write-life hints, inode cache lifetime, XFS tracepoints, and mount option `max_open_zones`.

## Risks and test signals
Risks include open-zone ref leaks, stale inode cached zones, zone append sector reporting, speculative GC/user write races, reclaim bucket drift, free counter inconsistency, conventional-zone write pointer approximation after power loss, and open-zone deadlocks. Test signals include sequential and conventional zoned devices, mount after unclean shutdown, tiny open-zone limits, write-life hint colocation, small-file pack-tight workloads, full-zone transitions, freeing blocks from open versus closed zones, and bio split failures.
