# sources/distributed-fs/openafs/src/afs/OBSD/osi_file.c

## Purpose
OpenBSD cache-file access layer for disk-backed OpenAFS cache entries stored as UFS files.

## Important APIs, Types, and Functions
Defines `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Uses `struct osi_file`, `struct osi_stat`, `afs_osi_credp`, `cacheDev`, and `afs_cacheVfsp`.

## Control Flow
`osi_UFSOpen` validates UFS cache type, allocates `osi_file`, drops `AFS_GLOCK`, resolves an inode with `VFS_VGET`, unlocks the vnode, records size and offset, and returns the wrapper. Stat/read/write/truncate drop the global lock before VOP or `vn_rdwr` calls, then reacquire it and update cached size/offset. Close releases the vnode and frees the wrapper.

## State and Persistence
Persistent bytes live in the cache file vnode. In-memory state is `osi_file` offset, size, callback proc, and global credential initialization flag. Read/write mutate the backing cache file and update wrapper position.

## Dependencies and Integration Points
Depends on OpenBSD VFS/VOP/vn_rdwr, UFS inode layout variants, `afs_osi_credp`, OpenAFS stats and tracing, and cache type selection via `cacheDiskType`.

## Risks
Kernel locking is delicate because vnode I/O occurs with `AFS_GLOCK` dropped. `osi_UFSOpen` panics on lookup failures, so cache corruption can take down the kernel module. Atime disabling is a stub, so cache reads may update access times. Error return convention converts positive errno to negative byte counts for read/write callers.

## Test Signals
Open, stat, read, write, truncate, and close cache files; validate offsets and size tracking; simulate missing cache inode; verify shutdown clears credential initialization only on cold shutdown; run with lock diagnostics to catch GLOCK/VOP misuse.
