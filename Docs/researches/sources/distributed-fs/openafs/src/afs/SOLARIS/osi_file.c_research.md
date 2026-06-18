# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_file.c

## Purpose
Solaris cache-file access layer for disk-backed OpenAFS cache entries, supporting UFS, optional VXFS, and path-based cache vnode lookup.

## Important APIs, Types, and Functions
Defines `afs_InitDualFSCacheOps`, `VnodeToIno`, `VnodeToDev`, `VnodeToSize`, `osi_VxfsOpen`, `osi_UfsOpen`, `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`.

## Control Flow
Cache open initializes root credentials, chooses VXFS or UFS, and either looks up by path (`AFS_CACHE_VNODE_PATH`) or calls `igetinode`. Stat/truncate/read/write drop GLOCK around VOP or `vn_rdwr` calls. Reads update offsets and disable UFS atimes; writes update offsets and invoke callback procs. Dual FS detection uses `VFS_STATVFS` and `modlookup("vxfs", "vx_vp_byino")`.

## State and Persistence
Persistent bytes are Solaris cache vnodes. In-memory state includes `afs_osicred_initialized`, `afs_CacheFSType`, `vxfs_vx_vp_byino`, wrapper offsets/sizes/proc callbacks, and credential pointer `afs_osi_credp`.

## Dependencies and Integration Points
Depends on Solaris VFS/VOP, UFS inode helpers from `SOLARIS/osi_inode.c`, optional VXFS module symbols, root credentials, and OpenAFS cache type flags.

## Risks
Many failures panic, especially inode/path lookup failures during cache open. Atime disabling touches UFS internals and is disabled for vnode-path caches. VXFS and UFS symbol lookup are kernel-version sensitive. Path buffer is fixed at 1024 bytes.

## Test Signals
Open/read/write/stat/truncate cache files for UFS and path-backed cache, optional VXFS open if configured, atime suppression on UFS, missing cache file behavior, and cold shutdown reset of credential initialization.
