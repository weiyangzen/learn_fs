# sources/distributed-fs/openafs/src/afs/HPUX/osi_file.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_file.c

Purpose: implements HP-UX cache-file operations used by the AFS disk cache when the cache type is UFS. It opens cache inodes, stats/truncates cache files, and performs kernel-space reads and writes through vnode I/O.

Important APIs/types/functions: `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, and `shutdown_osifile`. It manages static `afs_osi_cred` and `afs_osicred_initialized`, uses `cacheDev`, `afs_cacheVfsp`, `igetinode`, `VOP_GETATTR`, `VOP_SETATTR`, `gop_rdwr`, and `struct osi_file`.

Control flow: `osi_UFSOpen` verifies UFS cache type, initializes a held static credential, allocates `osi_file`, drops the AFS global lock around `igetinode`, panics on inode lookup failure, unlocks the inode, and stores vnode/size/offset. Reads and writes optionally set the file offset, drop `AFS_GLOCK` around `gop_rdwr`, update offset by transferred bytes, and convert positive kernel errors into negative OpenAFS-style returns. Reads retry up to five times on `EFAULT`; writes warn on `ENOSPC` and invoke an optional completion callback.

State/persistence: persistent state is the UFS cache file contents and inode attributes. `osi_UFSTruncate` only shrinks files after a stat check, temporarily swaps process credentials because HP-UX UFS consults `u.u_cred`, and restores credentials afterward. `osi_DisableAtimes` suppresses atime writes by clearing `IACC`.

Dependencies/integration: depends on HP-UX UFS inode/vnode behavior, `afs/osi_inode.h`, OpenAFS stats/tracing, global lock transitions, and current process credential APIs.

Risks/test signals: high risks are credential swapping, panic-on-open-failure semantics, EFAULT retry masking, offset accounting after partial I/O, and atime suppression. Test cache open/read/write/truncate/close, low-space writes, cache inode disappearance, shutdown with null file reads, and HP-UX UFS credential behavior.
