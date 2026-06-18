# sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.c

## Purpose
Resolves FreeBSD UFS inode numbers into kernel inode/vnode objects for cache-file access and stubs unsupported inode syscalls.

## Important APIs, Types, And Functions
`getinode` locates a mounted UFS filesystem and calls `VFS_VGET`. `igetinode` validates allocated regular inodes. `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec` return `EOPNOTSUPP`.

## Control Flow
If no mount is supplied, `getinode` scans the mount list under `mountlist_mtx` for a UFS mount matching the device, then calls `VFS_VGET`. `igetinode` rejects zero-mode, zero-link, or non-regular inodes, releasing the vnode on failure and returning the inode pointer on success.

## State And Persistence
No local persistent state. It observes host UFS inode fields such as `i_mode` and `i_nlink`.

## Dependencies And Integration Points
Depends on FreeBSD UFS structures, mount list locking, cdev device identity, and cache-file code that needs inode-to-vnode conversion.

## Risks
The implementation is tied to UFS internals and does not support non-UFS cache filesystems. Mount-list iteration and `VFS_VGET` signatures vary across FreeBSD versions. Unsupported inode syscalls must not be required by modern callers.

## Test Signals
Open valid and invalid cache inodes, deleted inodes, non-regular files, and absent devices. Build against target FreeBSD UFS headers.
