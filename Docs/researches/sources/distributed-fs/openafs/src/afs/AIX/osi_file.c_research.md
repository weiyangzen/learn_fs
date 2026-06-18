# sources/distributed-fs/openafs/src/afs/AIX/osi_file.c

Purpose: AIX UFS cache-file access layer for OpenAFS disk cache operations.

Important APIs and functions: `osi_UFSOpen` opens a cache inode by device/inode and returns `struct osi_file`; `afs_osi_Stat` fetches size/mtime/atime; `osi_UFSClose` releases vnodes and may flush VM pages under page pressure; `osi_UFSTruncate` shrinks cache files; `afs_osi_Read` and `afs_osi_Write` call `gop_rdwr`; `osi_DisableAtimes` clears access-time updates; `afs_osi_MapStrategy` forwards buffer strategy calls; `shutdown_osifile` resets static credentials on cold shutdown.

Control flow: cache opens validate `cacheDiskType`, initialize a static credential, drop `AFS_GLOCK` around inode lookup, then store vnode/size/offset in `osi_file`. Reads and writes optionally seek by updating `afile->offset`, drop the global lock during VNOP I/O, and convert residuals to byte counts.

State and persistence: tracks static `afs_osi_cred`, `afs_osicred_initialized`, per-file vnode/offset/size/proc callback, and real UFS cache file contents.

Dependencies and integration: uses AIX inode helpers from `osi_inode.c`, `gop_rdwr` from `osi_misc.c`, VM helpers, AFS tracing/statistics, and global cache device/vfs state.

Risks and test signals: `osi_UFSOpen` panics on lookup failure; read retries mask transient `EFAULT`; write ENOSPC warns via AFS. Signals include cache read/write byte counts, trace events, ENOSPC warnings, and stable cache truncation behavior.
