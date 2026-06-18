# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.h

## Purpose
Defines the public superblock interface and the per-superblock BeeGFS mount state for the client module.

## Important APIs and Types
`FhgfsSuperBlockInfo` stores the embedded `App`, optional `backing_dev_info`, and root initialization flags. Constants include `BEEGFS_MAGIC` and reported statfs block size values. Public declarations expose filesystem registration, superblock fill/kill/put, and mount option display. Inline accessors expose `App`, BDI, root `EntryInfo` readiness, and root attribute initialization state.

## Control Flow
Most functions in this header are inline accessors used by VFS operations throughout the client. `FhgfsOps_getApp()` and `FhgfsOps_getBdi()` retrieve per-mount state from `sb->s_fs_info`; root flags are read/set by mount and inode lookup/revalidation paths.

## State and Persistence
The header defines in-memory mount state only. `haveRootEntryInfo` and `isRootInited` are process-lifetime flags tied to root inode metadata refresh behavior, not durable state. Comments specify lock expectations for root entry info: callers should coordinate with `fhgfsInode->entryInfoLock` except during mount.

## Dependencies and Integration Points
Includes `App`, common definitions, kernel VFS/BDI/seq APIs, and `FhgfsOps_versions.h` for cross-kernel signatures. The structure layout is consumed by `FhgfsOpsSuper.c` and all VFS paths that need the `App`.

## Risks
Inline getters intentionally skip null checks for performance. Any caller using them before successful superblock initialization or after partial teardown can dereference null state. Locking guidance around root flags is advisory, so misuse can produce stale root entry information.

## Test Signals
Compile across kernel feature combinations, mount failure paths that leave `s_fs_info` null, and root lookup/revalidation tests that check flag transitions under lock.
