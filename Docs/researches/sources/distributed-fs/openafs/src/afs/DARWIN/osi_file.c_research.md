# sources/distributed-fs/openafs/src/afs/DARWIN/osi_file.c

## Purpose
Implements Darwin cache-file operations for the OpenAFS disk cache. It opens cache vnodes by stored inode/path identity, reads and writes cache data, truncates cache files, obtains metadata, and detects the backing filesystem type.

## Important APIs, Types, And Functions
`afs_InitDualFSCacheOps` classifies HFS, UFS, or APFS cache backing. `VnodeToIno` and `VnodeToDev` extract stable vnode identifiers. `osi_UFSOpen`, `osi_UFSClose`, `osi_UFSTruncate`, `afs_osi_Stat`, `afs_osi_Read`, `afs_osi_Write`, `osi_DisableAtimes`, and `shutdown_osifile` implement the platform `osi_file` contract.

## Control Flow
Initialization inspects a sample cache vnode mount name once and records `afs_CacheFSType`. Opening validates UFS-style cache mode, creates a minimal `afs_osi_credp` if needed, drops the AFS global lock, resolves the vnode via `vnode_open`, `igetinode`, or path-backed cache configuration, reacquires the global lock, then fills an `osi_file`. Reads and writes update `afile->offset`, drop the global lock around `VNOP_READ`/`VNOP_WRITE` or `gop_rdwr`, translate residual counts into bytes transferred, and run completion callbacks after writes. Truncate first stats the file to avoid unnecessary shrinking work.

## State And Persistence
Persistent state includes global `afs_osicred_initialized`, `afs_osi_credp`, `afs_CacheFSType`, `cacheDev`, and `afs_cacheVfsp`. Each `osi_file` persists a vnode reference, current offset, cached size, and optional completion procedure. Backing cache files persist data and metadata in the host filesystem.

## Dependencies And Integration Points
Depends on Darwin vnode attributes, UBC/VNOP I/O, APFS/HFS/UFS identification, `osi_inode.c` inode resolution, OpenAFS small-space allocation, global lock release/reacquire discipline, and cache-manager callers that use `afs_osi_Read`/`Write`.

## Risks
Incorrect cache filesystem detection can make inode/device extraction panic or return wrong cache IDs. The static OSI credential is intentionally artificial and must be cleaned on cold shutdown. The code relies on dropping the global lock around vnode operations to avoid deadlocks. Residual handling, atime suppression, path-backed cache vnodes, and APFS/HFS/UFS conditionals are compatibility-sensitive.

## Test Signals
Exercise cache initialization on HFS/UFS/APFS where supported, cache file open by inode/path, read/write offset advancement, truncate-to-smaller behavior, stat results, cold shutdown credential cleanup, and failure paths where cache files vanish. Kernel logs should not show `UFSOpen` panics for valid cache entries.
