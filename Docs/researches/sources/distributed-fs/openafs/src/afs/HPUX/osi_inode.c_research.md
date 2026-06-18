# sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.c

Purpose: implements HP-UX UFS inode syscalls used by OpenAFS server/salvager tooling to create, open, and adjust special Vice cache/server inodes.

Important APIs/types/functions: `getinode`, `igetinode`, `iforget`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`. It uses HP-UX `iget`, `ialloc`, `iput`, `idrop`, `falloc`, vnode fileops, and inode fields defined in `osi_inode.h`.

Control flow: `getinode` resolves a mount from `vfsp` or `dev`, then calls `iget`. `igetinode` validates allocation, link count, and regular-file type before returning an inode, otherwise sets `u.u_error`. `afs_syscall_icreate` requires superuser, obtains root inode 2, allocates a nearby inode, initializes it as a regular file, sets Vice metadata fields, returns the inode number in `u.u_r.r_val1`, and releases it. `afs_syscall_iopen` validates privilege and inode, allocates a file descriptor, wires vnode-backed file state, increments write count for writable regular files, and calls `putf` for multithreaded processes. `afs_syscall_iincdec` validates Vice magic and volume parameter, adjusts link count, and clears magic when count reaches zero.

State/persistence: persists Vice metadata in repurposed HP-UX inode fields and mutates inode link counts/mode/flags. File descriptor state is installed in the current process.

Dependencies/integration: depends on HP-UX UFS internals, `u.u_error`, OpenAFS superuser checks, and inode field macros from `osi_inode.h`.

Risks/test signals: legacy K&R functions with missing explicit returns are fragile. Risks include inode field aliasing, wrong write-count accounting, link-count underflow, and root-only syscall exposure. Test salvager/fileserver inode create/open/inc/dec paths, multi-threaded descriptor use, invalid inode/dev handling, and non-Vice inode rejection.
