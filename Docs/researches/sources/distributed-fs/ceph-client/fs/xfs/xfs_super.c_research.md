# sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c` is the XFS VFS superblock and module lifecycle implementation. It parses mount options, opens and configures data/log/realtime devices, initializes per-mount workqueues/counters/stats, fills the Linux superblock, handles remount/freeze/statfs/sync/shutdown callbacks, and registers or unregisters global XFS caches, sysfs, procfs, sysctl, quota, workqueues, and the filesystem type. The source was read as a complete 2,721-line file for this report.

## Important APIs, Types, and Functions

Important public or integration-facing symbols include `xfs_set_inode_alloc`, `xfs_flush_inodes`, `xfs_reinit_percpu_counters`, `xfs_debugfs_mkdir`, `xfs_export_operations`, `xfs_quotactl_operations`, `xfs_discard_wq`, `init_xfs_fs`, and `exit_xfs_fs`. The main static machinery includes `xfs_fs_parameters`, `xfs_fs_parse_param`, `xfs_fs_validate_params`, `xfs_fs_fill_super`, `xfs_fs_get_tree`, `xfs_fs_reconfigure`, `xfs_remount_rw`, `xfs_remount_ro`, `xfs_super_operations`, `xfs_context_ops`, `xfs_fs_type`, cache/workqueue init/destroy helpers, DAX setup, device setup, statfs helpers, freeze/unfreeze helpers, inode lifecycle callbacks, and filesystem context allocation/freeing.

## Control Flow

Module load begins at `init_xfs_fs`: verify on-disk structures, run the directory hash test, initialize directory code, slab caches, global workqueues, MRU cache, procfs, sysctl, debugfs, sysfs kset, global stats, scrub stats, optional debug kobject, quota manager, and finally `register_filesystem`. Mount setup begins with `xfs_init_fs_context`, which allocates a mostly blank `struct xfs_mount`, initializes locks, xarrays, work items, defaults, hooks, and parser operations. Parameters are parsed by `xfs_fs_parse_param`, validated by `xfs_fs_validate_params`, and materialized by `xfs_fs_fill_super`.

During `xfs_fs_fill_super`, the code copies VFS flags into XFS feature state, opens devices, creates debugfs and per-mount workqueues, initializes percpu counters and inodegc state, allocates stats and scrub stats, reads the superblock, validates feature and geometry constraints, configures devices, reads realtime metadata, mounts filestream state, populates the Linux superblock, checks DAX/discard/zoned/reflink constraints, resumes quota flags when appropriate, calls `xfs_mountfs`, and installs the root dentry. Every failure path unwinds only the resources acquired up to that point.

Runtime VFS callbacks route through `xfs_super_operations`: sync forces the log and stops GC before freeze, freeze saves reserve blocks and quiesces the log, unfreeze restores reserves and restarts workers, statfs reports data or realtime free space plus quota adjustments, inode destroy queues reclaim, drop_inode protects recovery inodes, evict_inode tears down page cache/DAX and zoned private state, put_super unmounts and frees per-mount runtime resources, and shutdown forces device-removed shutdown.

Remount uses a fresh parsed mount context. `xfs_fs_reconfigure` validates the requested options, copies error tags, validates atomic write changes, updates inode32/inode64 allocation policy, reruns finish validation, and then dispatches ro-to-rw or rw-to-ro transitions. `xfs_remount_rw` restores reserves, restarts log/blockgc/inodegc/zonegc, and reserves per-AG metadata blocks; `xfs_remount_ro` syncs, stops GC, frees COW/prealloc space, unreserves AG blocks, saves reserve blocks, cleans the log, and marks the mount readonly.

## State and Persistence Behavior

Persistent state is the on-disk XFS superblock, realtime metadata, log, quota state, and feature flags read and modified by lower-level mount code. This file owns orchestration state: `struct xfs_mount`, feature bits, qflags, device targets, workqueue pointers, per-CPU counters, per-CPU stats, inodegc queues, debugfs/sysfs objects, and module-global slab caches/workqueues/ksets. Freeze/remount paths explicitly save and restore reservation pool state. Mount options such as quota flags, DAX mode, inode allocation mode, discard, zoned limits, and atomic write limits affect runtime behavior and sometimes trigger superblock updates through lower layers.

## Dependencies and Integration Points

This file integrates nearly every major XFS subsystem: superblock reading/freeing, log recovery and forcing, inode cache/reclaim, buffer targets, allocation groups, quotas, realtime/zoned allocation, filestreams, scrub stats, health monitoring, parent pointers, deferred ops, reflink, DAX, sysfs/procfs/sysctl/debugfs, VFS fs_context, block device open/flush/invalidate, shrinkers, freeze infrastructure, and module registration. It calls into `xfs_stats.c`/`xfs_sysfs.c` indirectly through stats allocation and module sysfs setup.

## Risks and Edge Cases

Mount and module init are high-risk because the unwind ladder must exactly mirror acquisition order. Device identity checks prevent realtime/log/data aliasing, and `xfs_shutdown_devices` flushes and invalidates bdev page cache to avoid stale metadata reads by userspace tools. Option validation must reject incompatible combinations such as `norecovery` rw mounts, `noalign` with stripe options, invalid log buffer sizes, unsupported quotas, zoned-only options on non-zoned filesystems, unsupported V4/ascii-ci formats, needs-repair filesystems without norecovery, and block sizes outside platform limits. DAX is disabled or rejected depending on device, blocksize, reflink, and partition state. Remount currently ignores many immutable option changes by design, so tests should distinguish accepted-but-ignored options from real state changes.

## Test Signals

Strong signals include kernel builds across `CONFIG_XFS_QUOTA`, `CONFIG_XFS_RT`, `CONFIG_FS_DAX`, `CONFIG_XFS_SUPPORT_V4`, `CONFIG_XFS_SUPPORT_ASCII_CI`, debug, scrub, and repair combinations; fstests mount/remount/freeze/unfreeze/statfs coverage; failure-injection of each mount-stage allocation and device open path; ro/rw remount tests with external log and realtime devices; DAX/discard/zoned/reflink compatibility tests; module load/unload leak checks; and sysfs/procfs/debugfs presence checks after mount and unmount.
