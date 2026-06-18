# sources/distributed-fs/openafs/src/afs/AIX/osi_inode.c

Purpose: AIX inode support for OpenAFS server/salvager style inode operations and cache inode lookup.

Important APIs and functions: `devtovfs` locates a mounted JFS vfs by device; `igetinode` validates and returns an inode/vnode; syscall wrappers `icreate`, `iopen`, and `iincdec` are generated through `SYSENT`; convenience `iinc` and `idec` adjust link counts.

Control flow: `SYSENT` wraps syscall bodies in `setjmpx`/`clrjmpx` and converts kernel exceptions to `uerror`. `igetinode` locates a vfs, rejects inode 0, locks JFS icache, calls imported `iget`, verifies nonzero link count and regular-file mode, and returns an associated vnode. `icreate` requires superuser, allocates a regular inode, stamps `VICEMAGIC` and vice fields, then releases the vnode. `iopen` creates a file descriptor over the vnode and opens it. `iincdec` validates `VICEMAGIC` and vicep1 before changing `i_nlink` and committing.

State and persistence: persists vice metadata in reserved inode fields, changes inode link counts, and records diagnostic globals `IGI_error`, `IGI_inode`, `IGI_nlink`, and `IGI_mode`.

Dependencies and integration: uses imported JFS functions from `osi_config.c`, macros from `osi_inode.h`, AIX vnode/file descriptor APIs, and superuser checks.

Risks and test signals: inode lock field offsets are version-sensitive; bad inode 0 handling could panic AIX; direct link-count mutation requires exact `VICEMAGIC` semantics. Signals include successful salvager/server inode syscalls and no `BAD_IGET` diagnostics.
