# sources/cloud-native/nydus/service/src/upgrade.rs

Purpose: manages online-upgrade state transfer for fscache and FUSE daemons. It serializes service state through a `nydus_upgrade` storage backend over Unix domain socket and preserves one critical fd for the next process.

Important APIs/types: `UpgradeMgrError`, `FailoverPolicy`, internal `FscacheState`, `MountStateWrapper`, `FusedevState`, `UpgradeManager`, `fscache_upgrade::{BlobCacheEntryState,FscacheBackendState,save,restore}`, and `fusedev_upgrade::{FusedevBackendState,save,restore}`.

Control flow: concrete services update `UpgradeManager` as blobs are added/removed, fscache path/thread count changes, VFS state is saved, mounts are added/updated/removed, and fuse connection id is known. `save` sends serialized bytes plus held fd to `UdsStorageBackend`; `restore` receives fds and state bytes. Fscache restore rebuilds blob entries and reinitializes `FsCacheHandler` with the restored cachefiles fd. FUSE restore restores connection id, fuse fd, drains pending requests, restores VFS bytes, and replays saved mounts by VFS index.

State and persistence: fscache state is a map of `domain/blob` to serialized `BlobCacheEntry`, thread count, and path. FUSE state is mountpoint to mount command/index, VFS snapshot bytes, and fuse connection id. The held `File` is cloned from the active cachefiles/fuse fd and returned as a clone during restore.

Dependencies and integration: integrates `nydus_upgrade::StorageBackend`, `UdsStorageBackend`, versionize snapshotters, `BlobCacheEntry`, `Vfs::save_to_bytes`/`restore_from_bytes`, `ServiceController`, `FusedevDaemon`, and `FsService::restore_mount`.

Risks: restore assumes exactly at least one fd and indexes `fds[0]`; missing supervisor path prevents restore; stale source/config paths in saved mount commands break replay; VFS and mount snapshot versions must remain compatible; FUSE drain failures are logged but restore continues.

Test signals: tests cover failover-policy parsing for `none`, `flush`, and `resend`; fscache state conversion/serialization and blob entry removal; FUSE mount state conversion/update/removal and fuse cid; and fd hold/return cloning.
