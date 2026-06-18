# sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.c

## Purpose
Resolves host filesystem inodes into vnodes for Darwin cache-file access and stubs unsupported inode syscalls.

## Important APIs, Types, And Functions
`getinode` opens a vnode by device and inode, using `/.vol/<dev>/<inode>` with `vnode_open` on Darwin 8+ or `VFS_VGET`/mount-list search on older kernels. `igetinode` validates type, mode, nlink, and attributes before returning a cache vnode. `iforget` handles older vnode disposal. `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec` return unsupported errors.

## Control Flow
Modern Darwin constructs a `/.vol` path, opens it read/write in the AFS OSI context, validates the vnode type, fetches mode/nlink/size with `vnode_getattr`, rejects unallocated or unlinked entries, and returns the vnode. Older Darwin searches mounted UFS/HFS filesystems if no mount was supplied, calls `VFS_VGET`, validates `v_type`, attributes, and links, then unlocks or releases the vnode as needed.

## State And Persistence
The file does not persist its own data. It relies on host filesystem inode metadata and on global cache mount/device state passed by callers.

## Dependencies And Integration Points
Depends on Darwin vnode, mount, UFS/HFS internals for older kernels, `afs_osi_credp`, `afs_CacheFSType`, and `osi_file.c` cache open paths.

## Risks
The `/.vol` path representation and device/inode formatting must match Darwin behavior. Older mount-list scanning is fragile across filesystem implementations. Returning invalid, unlinked, or wrong-type vnodes would corrupt cache access. The unsupported inode syscalls must remain unreachable or callers must handle `ENOTSUP`/`EOPNOTSUPP`.

## Test Signals
Open valid and deleted cache files by inode, verify bad type/mode/nlink rejection, exercise HFS/UFS older paths if built, and confirm unsupported inode syscalls fail cleanly.
