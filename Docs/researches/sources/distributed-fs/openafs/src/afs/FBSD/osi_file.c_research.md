# sources/distributed-fs/openafs/src/afs/FBSD/osi_file.c

## Purpose
Implements FreeBSD cache-file I/O for OpenAFS, including opening cache vnodes by inode, stat/read/write/truncate operations, atime suppression, and shutdown reset.

## Important APIs, Types, And Functions
Exports `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`.

## Control Flow
`osi_UFSOpen` validates UFS cache mode, allocates `osi_file`, drops the AFS global lock, calls `VFS_VGET`, rejects `VNON`, unlocks the vnode, and records size/offset. Stat and truncate lock the cache vnode around `VOP_GETATTR`/`VOP_SETATTR`. Read/write set the offset, drop the global lock around `gop_rdwr`, convert residuals to bytes transferred, update the offset, and trace negative errors. MapStrategy simply invokes the supplied strategy routine.

## State And Persistence
Global state includes `afs_osicred_initialized`, `cacheDev`, and `afs_cacheVfsp`. Per-open state is the `osi_file` vnode, size, offset, and completion callback. The host UFS file persists cached data.

## Dependencies And Integration Points
Depends on FreeBSD vnode, UFS inode, `vn_rdwr` through `gop_rdwr`, OpenAFS global lock, cache manager `osi_file` contract, and FreeBSD credential `afs_osi_credp`.

## Risks
The code assumes UFS inode internals (`VTOI(vp)->i_size`, `IN_ACCESS`). Lock dropping around vnode I/O must be balanced. Reads during shutdown return `-EIO` instead of panicking, but other null write paths panic. Version-dependent residual type matters.

## Test Signals
Open cache files, read/write data and offsets, truncate only when shrinking, stat metadata, suppress atime changes, invoke write callbacks, and run warm/cold shutdown without credential-state corruption.
