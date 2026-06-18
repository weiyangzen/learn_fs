# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.c

## Purpose
Solaris UFS inode syscall support for OpenAFS server/cache inode operations, including inode creation, open-by-inode, and link-count increment/decrement.

## Important APIs, Types, and Functions
Defines `getinode`, `igetinode`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`. Uses UFS function pointers `ufs_iallocp`, `ufs_iupdatp`, `ufs_igetp`, `ufs_itimes_nolockp`, plus `CrSync` and `IncSync`.

## Control Flow
`getinode` resolves a VFS by device, enters quota lock if present, and calls `ufs_iget`. `igetinode` validates allocation, link count, and regular-file mode, optionally adds a fake DNLC entry. `icreate` checks superuser, opens root inode, allocates a new inode near a hint, stamps VICEMAGIC and vice metadata fields, syncs, and returns the inode number. `iopen` opens an existing inode into a file descriptor. `iincdec` validates VICEMAGIC, adjusts link count, clears magic on zero, and syncs if configured.

## State and Persistence
Mutates persistent UFS inode metadata: mode, link count, vice fields, timestamps, and magic values. Also creates process file descriptors for opened inodes and DNLC aliases.

## Dependencies and Integration Points
Depends on Solaris UFS internals and symbols resolved in `SOLARIS/osi_vfsops.c`, credential privilege checks, vnode/file descriptor APIs, and `SOLARIS/osi_inode.h` macros.

## Risks
This code reaches deep into UFS private structures and symbol pointers; missing symbols degrade functionality. Incorrect vice field packing can orphan cache/server data. Superuser checks gate destructive inode operations. Endianness and 32/64-bit rval handling are sensitive.

## Test Signals
Privileged icreate/iopen/iincdec round trips, non-root EPERM, link count decrement to zero clearing VICEMAGIC and DNLC alias, 32-bit and 64-bit syscall return values, and missing UFS symbol warnings at module init.
