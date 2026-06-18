# sources/distributed-fs/ceph-client/fs/ntfs/super.c

## Purpose
Implements the legacy `ntfs` filesystem module's superblock lifecycle: mount option parsing, boot-sector validation, mount-time volume bootstrap, system-file loading, free-space accounting, sync/unmount behavior, error policy, sysctl/slab/workqueue setup, and filesystem registration. It is the central integration point between VFS superblock operations and NTFS on-disk metadata such as `$MFT`, `$MFTMirr`, `$Bitmap`, `$Volume`, `$LogFile`, `$UpCase`, `$AttrDef`, `$Secure`, `$Extend`, and `$Quota`.

## Important APIs, Types, And Functions
`ntfs_parse_param()` maps fs context options into `struct ntfs_volume`, including identity masks, NLS charset, error policy, sparse/discard/system-file visibility, ACLs, and case behavior. `ntfs_reconfigure()` handles read-only/read-write remount transitions and enforces dirty, chkdsk, logfile, quota, and unsupported-flag checks. `ntfs_handle_error()` applies the configured error policy. Persistent metadata helpers include `ntfs_write_volume_flags()`, `ntfs_set_volume_flags()`, `ntfs_clear_volume_flags()`, and `ntfs_write_volume_label()`.

Mount bootstrap flows through `ntfs_fill_super()`, which reads and parses the boot sector, sets VFS superblock fields, constructs the special `$MFT` inode, initializes global/default upcase state, loads system files with `load_system_files()`, creates the root dentry, starts background free-cluster precalculation, and registers `ntfs_sops`. The system-file helpers validate `$MFTMirr`, `$LogFile`, hibernation state, quotas, `$AttrDef`, `$UpCase`, `$Bitmap`, `$Volume`, `$Secure`, and `$Extend`. `ntfs_put_super()`, `ntfs_sync_fs()`, `ntfs_shutdown()`, and `ntfs_force_shutdown()` implement flush, clean-bit handling, block-device flush, and shutdown state.

## Control Flow
Mount starts with an allocated `ntfs_volume` from `ntfs_init_fs_context()`. After option parsing, `get_tree_bdev()` calls `ntfs_fill_super()`: validate device sector size, read the primary boot sector, derive cluster/MFT/index geometry, initialize allocator cursors, create `$MFT`, load all required metadata files, then install the root dentry. Failure paths unwind in reverse order and release upcase, NLS, bitmap counters, and inodes. Remount first syncs the filesystem, then allows read-write only if error/dirty/chkdsk/logfile/quota checks pass. Unmount commits metadata in dependency order, clears the dirty bit when safe, flushes the block device, drops inodes, and frees volume-scoped memory.

## State And Persistence
Persistent writes include `$Volume` flags, volume label replacement, logfile emptying, quota out-of-date marking, inode/MFT commits, dirty-bit clearing, and block-device flushes. In-memory state includes `default_upcase` plus a global user count guarded by `ntfs_lock`, mount option flags in `vol->flags`, atomic free cluster/MFT counters, dirty cluster reservation, `lcn_empty_bits_per_page`, and a background work item for bitmap scanning. Free-space accounting pessimistically treats unreadable bitmap pages as allocated.

## Dependencies And Integration Points
This file integrates with VFS `fs_context`, `super_operations`, slab caches, workqueues, block-device APIs, NLS, errseq writeback tracking, NTFS inode/attribute/index/logfile/quota/security code, and mount option display in inode code. It also calls into `sysctl.c` during module init/exit when debug sysctls are compiled.

## Risks And Edge Cases
Mount safety depends on conservative refusal of unsupported geometry, dirty volumes, hibernated Windows volumes, bad `$MFTMirr`, bad logfile state, and unsupported volume flags. Error unwinds are complex and must avoid leaks or double releases, especially around `default_upcase` sharing and partially loaded system files. `check_mft_mirror()` compares metadata and constructs expected runlists; mismatches degrade to read-only or error state. Free cluster counting waits on `NVolFreeClusterKnown`, so initialization order and wakeups are important. Dirty-bit clearing during sync/unmount is a persistence risk if metadata writeback silently failed.

## Test Signals
Exercise clean read-write mounts, dirty/chkdsk/hibernated volumes, unsupported sector/cluster/MFT record sizes, remount ro/rw transitions, invalid NLS names, volume label updates, logfile-empty failures, quota absence/presence, `$MFTMirr` mismatch, statfs before and after background free-space scan, shutdown ioctls, discard unsupported devices, and module init failure injection for each slab/sysctl/workqueue step.
