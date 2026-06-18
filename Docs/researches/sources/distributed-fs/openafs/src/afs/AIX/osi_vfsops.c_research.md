# sources/distributed-fs/openafs/src/afs/AIX/osi_vfsops.c

Purpose: AIX VFS operation table and mount/root/stat/vget behavior for the AFS filesystem.

Important APIs and functions: `afs_mount`, `afs_unmount`, `afs_root_nolock`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afs_aix_badop`, and exported `Afs_vfsops`.

Control flow: mount takes the AFS global lock if needed, rejects remounts and file-over-file mounts, initializes vfs fields/fsid, marks remote mount data, attempts root vnode setup, and registers iauth when configured. Root lookup initializes a request, checks AFS initialization, gets the root vcache, marks it `VROOT`, stores it in `afs_globalVp`, and assigns `vfs_mntd`. Unmount clears `afs_globalVFS` and calls cold shutdown. `afs_vget` converts a fileid to a vcache through `afs_osi_vget`.

State and persistence: `afs_globalVFS` and `afs_globalVp` hold process-wide mount/root state. Statfs returns fake free-space values, not persisted filesystem capacity.

Dependencies and integration: installed by `osi_config.c`, uses common AFS request/vcache/check-code paths, AIX VFS structs, and optional NFS exporter/iauth integration.

Risks and test signals: remount is intentionally rejected; root vcache caching must handle initialization races; statfs reports synthetic capacity. Signals include successful `/afs` mount/root lookup, `vget` by fileid, and clean cold unmount.
