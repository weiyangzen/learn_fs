## sources/distributed-fs/openafs/src/afs/NBSD/osi_file.c

Purpose: NetBSD UFS cache-file I/O helpers used by OpenAFS disk-cache code.

Important APIs and state: defines `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Global `afs_osicred_initialized` is reset during cold shutdown. `osi_file` instances hold a vnode, cached size, offset, optional completion callback, and proc pointer.

Control flow: `osi_UFSOpen` verifies UFS cache mode, allocates an `osi_file`, drops GLOCK, uses `VFS_VGET` on `cacheDev.mp` and the supplied inode, rejects `VNON`, unlocks the vnode, and initializes offset/size. Stat/getattr, truncate/setattr, read, and write all drop GLOCK around NetBSD vnode operations. Reads and writes use `vn_rdwr` with `AFS_UIOSYS`, `IO_UNIT`, `afs_osi_credp`, and `osi_curproc`; successful calls advance `afile->offset`, and writes update cached size. Truncate first stats and only shrinks if needed. Close releases the vnode and frees the small-space allocation.

Dependencies and integration: depends on NetBSD vnode/VFS operations, FFS inode size (`VTOI(vp)->i_ffs1_size`), OpenAFS cache device state, credentials, stats counters, tracing, and GLOCK discipline. It is the platform backend for the OpenAFS UFS disk cache.

State and persistence: reads/writes/truncates actual cache files on the local filesystem. `afile->offset` and `afile->size` mirror current per-open state. `shutdown_osifile` clears credential initialization on cold shutdown.

Risks: `osi_UFSOpen` panics on failed inode lookup, which is severe if cache metadata is corrupt. GLOCK must not be held across blocking vnode I/O. `osi_DisableAtimes` is a no-op, so cache reads may still affect atime depending on NetBSD behavior. Positive vnode errors are converted to negative return values in read/write paths.

Test signals: UFS cache open/stat/read/write/truncate/close, corrupt or missing cache inode behavior, shutdown cold vs warm, short read/write residual accounting, callback invocation after write, and cache consistency after vnode I/O errors.
