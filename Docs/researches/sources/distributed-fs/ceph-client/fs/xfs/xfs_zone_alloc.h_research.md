# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.h

## Purpose
`xfs_zone_alloc.h` declares the public zoned XFS allocation interface used by iomap writeback, realtime free-space accounting, mount/unmount, stats, and garbage collection control paths.

## Important APIs, types, and functions
It defines `struct xfs_zone_alloc_ctx` with an open-zone pointer and reserved block count, reservation flags `XFS_ZR_GREEDY`, `XFS_ZR_NOWAIT`, and `XFS_ZR_RESERVED`, and declarations for zoned space reserve/unreserve, availability updates, write submission, end-io remap, block free, open-zone put, wakeups, block-validity checks, stats, default reserved blocks, and mount/GC lifecycle.

## Control flow
Callers reserve zoned realtime space into an allocation context, submit writes via `xfs_zone_alloc_and_submit`, complete them through `xfs_zoned_end_io`, and unreserve any unused context state. Mount code calls `xfs_mount_zones` only when realtime support is present; otherwise stubs reject zoned mounting.

## State and persistence
The header has no storage, but its APIs manage open-zone references, free counters, rmap used counters, and persistent file mappings.

## Dependencies and integration points
It links XFS writeback, realtime allocation, zoned GC, sysfs/stat output, and mount feature checks. The `CONFIG_XFS_RT` conditional prevents accidental zoned operation without realtime support.

## Risks and test signals
Risks include caller leaks of `open_zone`, mismatched reserve/unreserve flags, and build behavior with `CONFIG_XFS_RT` disabled. Tests should cover reserve failure unwinds, nowait behavior, and non-RT build stubs.
