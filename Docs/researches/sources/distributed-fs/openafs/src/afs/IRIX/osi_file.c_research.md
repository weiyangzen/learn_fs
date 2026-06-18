# sources/distributed-fs/openafs/src/afs/IRIX/osi_file.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_file.c

Purpose: implements IRIX cache-file operations for AFS UFS-type disk cache, backed by XFS vnode lookup and generic vnode I/O.

Important APIs/types/functions: `afs_XFSIGetVnode`, `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Uses `xfs_igetinode`, `XFS_ITOV`, `AFS_VOP_GETATTR`, `AFS_VOP_SETATTR`, `gop_rdwr`, `VnodeToSize`, static `afs_osi_cred`, `cacheDev`, and `afs_cacheVfsp`.

Control flow: open verifies UFS cache type, initializes a held static credential, allocates `osi_file`, drops `AFS_GLOCK`, resolves the cache inode to an XFS vnode, restores the lock, and records vnode size/offset. Stat/truncate call IRIX VOP wrappers with attribute masks. Read/write build kernel-space vnode I/O through `gop_rdwr`, update offsets on success, trace read errors, return negative errors for failures, and call optional completion callbacks after writes.

State/persistence: persistent cache data lives in XFS files addressed by inode number. Truncation shrinks files via `AFS_VOP_SETATTR`. File offsets and optional callbacks are per-`osi_file` in-memory state.

Dependencies/integration: depends on IRIX XFS inode helpers from `osi_inode.c`, behavior-safe VOP macros from `osi_vfs.h`, and OpenAFS global lock transitions.

Risks/test signals: risks include panics on missing cache inodes, mismatch between UFS cache naming and XFS-only implementation, negative error conversion, and static credential lifetime. Test cache open/stat/read/write/truncate/close, missing inode handling, XFS cache devices, and shutdown reset.
