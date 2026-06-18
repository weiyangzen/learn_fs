# sources/distributed-fs/ceph-client/fs/ubifs/super.c

## Purpose
`super.c` implements UBIFS module initialization, filesystem registration, VFS superblock operations, fs_context parsing, mount/remount/unmount lifecycle, inode allocation/loading/freeing, writeback hooks, statfs/sync behavior, and the top-level orchestration of all UBIFS subsystems. It is the main bridge between Linux VFS/UBI and UBIFS internals.

## Important APIs, Types, And Functions
The VFS inode path is centered on `ubifs_iget()`, `validate_inode()`, `ubifs_alloc_inode()`, `ubifs_free_inode()`, `ubifs_write_inode()`, `ubifs_evict_inode()`, and `ubifs_dirty_inode()`. These functions translate UBIFS inode nodes into VFS inodes, validate on-flash fields, install file/dir/symlink/special inode operations, handle xattr and symlink inline data, write dirty inodes through the journal, and delete orphaned inodes.

Mount setup is handled by `init_constants_early()`, `init_constants_sb()`, `init_constants_master()`, `alloc_wbufs()`, `check_volume_empty()`, and `mount_ubifs()`. `mount_ubifs()` coordinates debugging, sysfs registration, empty-volume formatting, buffer allocation, authentication, superblock/master/LPT reads, recovery, journal replay, orphan mounting, free-space checks, log consolidation, GC LEB reservation, debugfs, and `ubifs_infos` registration.

Remount/unmount paths are `ubifs_remount_rw()`, `ubifs_remount_ro()`, `ubifs_reconfigure()`, `ubifs_put_super()`, and `ubifs_umount()`. VFS registration and fs_context paths are `open_ubi()`, `alloc_ubifs_info()`, `ubifs_fill_super()`, `ubifs_get_tree()`, `kill_ubifs_super()`, `ubifs_init_fs_context()`, and `ubifs_free_fc()`. Module lifecycle is `ubifs_init()` and `ubifs_exit()`, which create the inode slab, register the shrinker, initialize compressors/sysfs/debugfs, and register/unregister the filesystem.

## Control Flow
First mount parses options into `struct ubifs_fs_context`, opens the UBI volume read-only for identity lookup, allocates `struct ubifs_info`, and either reuses an existing superblock or calls `ubifs_fill_super()`. `ubifs_fill_super()` reopens UBI read-write, sets VFS fields, and calls `mount_ubifs()` under `umount_mutex`. After the internal mount succeeds, it reads the root inode, creates `s_root`, and publishes UUID/sysfs names.

`mount_ubifs()` is staged with matching cleanup labels. It initializes immutable UBI-derived constants, registers per-mount sysfs, detects empty volumes, allocates mount buffers, initializes authentication if requested, reads/creates the superblock, validates compressors and derived constants, allocates commit/write buffers and journal heads, starts the background thread for writable mounts, reads master/LPT state, performs recovery or marks the master dirty, writes pending superblock changes, replays the journal, mounts orphans, checks free/log space, handles GC LEB state, adds the instance to `ubifs_infos`, and runs debug checks.

Remount-rw allocates write-only resources that read-only mounts skip, completes deferred recovery, writes the master dirty flag, writes pending superblock changes, starts the background thread, initializes writable LPT state, and unmaps or commits the GC LEB. Remount-ro stops the thread, syncs write buffers, clears the dirty master flag, records no-orphans and GC LEB state, frees writable-only buffers, and drops writable LPT resources. Unmount follows a similar clean path unless the filesystem has already entered read-only error mode.

## State And Persistence
`struct ubifs_info` is the core in-memory state object. `alloc_ubifs_info()` initializes locks, wait queues, trees, lists, default mount settings, UBI geometry, and baseline logical positions. Persistent state affected by this file includes inode nodes written through journal operations, master-node dirty/no-orphans/gc fields, superblock writes delegated to `sb.c`, LPT state, log consolidation, recovery writes, and GC LEB unmapping. Mount flags such as `ro_mount`, `ro_media`, `need_recovery`, `ro_error`, `remounting_rw`, and `mounting` control which operations may write media and how aggressively node CRCs are checked elsewhere.

## Dependencies And Integration Points
The file integrates with VFS (`super_operations`, inode operations, fs_context, `sget_fc`, `kill_anon_super`), UBI open/close and sync APIs, Linux writeback and shrinker APIs, fscrypt, xattrs, sysfs/debugfs, compressors, authentication, journal, replay, recovery, LPT, master node handling, orphan handling, budgeting, GC, TNC, and background commit threads. It exports `ubifs_super_operations` and registers the `ubifs` filesystem type with `MODULE_ALIAS_FS("ubifs")`.

## Risks And Edge Cases
Mount and remount error unwinding is complex because different resources are allocated depending on read-only state, authentication, recovery need, and mount progress. Clean unmount must write master state unless the filesystem is already in read-only error mode. Deferred recovery for read-only mounts must complete correctly on later remount-rw. Option parsing ignores authentication changes on remount, so callers must not expect key replacement there. Empty volumes cannot be formatted if the mount or media is read-only. Inode validation prevents malformed media from creating impossible VFS state; bypassing it risks memory safety and filesystem corruption.

## Test Signals
Important tests include empty-volume formatting, normal mount, read-only mount, static/corrupt UBI volume handling, remount ro/rw with and without deferred recovery, mount option persistence and display, authentication options, bulk-read allocation failure fallback, inode loading for each file type, writeback of dirty inodes, orphan inode eviction, syncfs committing and UBI sync, statfs reserved-pool accounting, mount failure at each staged allocation point, and module init/exit registration cleanup.
