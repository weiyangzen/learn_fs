# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.c

## Purpose
Implements BeeGFS client VFS superblock registration, per-mount `App` lifecycle, root inode construction, procfs attachment, xattr handler selection, and unmount cleanup. It is the mount/unmount spine connecting Linux VFS objects to the BeeGFS runtime.

## Important APIs and Functions
`FhgfsOps_registerFilesystem()` and `FhgfsOps_unregisterFilesystem()` register the `file_system_type`. `FhgfsOps_fillSuper()` builds a mounted superblock and root dentry. `FhgfsOps_putSuper()` and `FhgfsOps_killSB()` tear down mount state. Private helpers `__FhgfsOps_constructFsInfo()`, `__FhgfsOps_destructFsInfo()`, `__FhgfsOps_initApp()`, and `__FhgfsOps_uninitApp()` allocate `FhgfsSuperBlockInfo`, run/stop `App`, create/remove procfs entries, and manage backing-device information.

## Control Flow
Mount registration points either `.get_sb` or `.mount` at the compatibility wrappers in `FhgfsOps_versions.c`, with `.kill_sb` bound to `FhgfsOps_killSB()`. `FhgfsOps_fillSuper()` calls `__FhgfsOps_constructFsInfo()`, which allocates `sb->s_fs_info`, parses raw mount options into `MountConfig`, initializes/runs `App`, creates per-mount procfs entries, and initializes BDI state where required. The fill path then configures VFS limits, flags, super operations, xattr handlers, export ops, root `kstat`, dummy `EntryInfo`, root inode, root dentry, and optional default dentry ops. Unmount disables connection retries, flushes page work, unregisters older BDI state, and lets `kill_anon_super()` drive `put_super`.

## State and Persistence
State is per mount and lives in `sb->s_fs_info`: embedded `App`, optional `backing_dev_info`, `haveRootEntryInfo`, and `isRootInited`. Procfs entries persist for the mount session and are removed after `App_stop()`. Root inode state is initially dummy and refreshed later by lookup/revalidation paths. No durable storage is written here; persistent effects are remote cluster/session side effects owned by `App`.

## Dependencies and Integration Points
Depends on VFS superblock APIs, `App`, `MountConfig`, `Config`, `ProcFs`, inode/file/dir/page/export operations, xattr handler arrays, `RWPagesWork`, and remoting helpers. It integrates with Linux BDI APIs across kernel versions and with NFS export support for supported kernels.

## Risks
Failure unwinding must keep `sb->s_fs_info`, `App`, BDI registration, root inode/dentry, and procfs entries balanced. `FhgfsOps_getApp()` assumes initialized `s_fs_info`, so callers during failed mounts must guard. Xattr handler selection depends on config combinations; wrong selection can silently disable ACL/SELinux paths. Unmount latency depends on connection retry state and page-work flushing.

## Test Signals
Useful tests include mount with valid/invalid options, BDI setup failure injection, procfs entry presence/removal, ACL/SELinux/xattr option combinations, root inode creation failure, repeated mount/unmount, unmount during communication failure, and stat/export smoke tests after mount.
