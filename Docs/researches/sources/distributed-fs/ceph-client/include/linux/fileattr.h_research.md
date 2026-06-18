# sources/distributed-fs/ceph-client/include/linux/fileattr.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fileattr.h` provides the merged VFS representation for legacy `FS_IOC_GETFLAGS/SETFLAGS` and XFS-style `FS_IOC_FSGETXATTR/FSSETXATTR` file attributes. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

Important masks are `FS_COMMON_FL`, `FS_XFLAG_COMMON`, `FS_XFLAG_RDONLY_MASK`, `FS_XFLAG_VALUES_MASK`, `FS_XFLAG_DIRONLY_MASK`, `FS_XFLAG_MISC_MASK`, and `FS_XFLAGS_MASK`. The central type is `struct file_kattr`. APIs include `copy_fsxattr_to_user`, `fileattr_fill_xflags`, `fileattr_fill_flags`, `fileattr_has_fsx`, `vfs_fileattr_get`, `vfs_fileattr_set`, `ioctl_getflags`, `ioctl_setflags`, `ioctl_fsgetxattr`, and `ioctl_fssetxattr`.

## Control Flow

Filesystem ioctl paths fill a `file_kattr` from either flags or fsxattrs, VFS validates and maps common bits, then get/set helpers call filesystem fileattr methods. `fileattr_has_fsx()` detects attributes that cannot be represented in simple flags.

## State and Persistence Behavior

`file_kattr` is transient request state. Persistent effects are filesystem inode flags, project IDs, extent size hints, CoW extent size hints, and read-only flags such as verity.

## Dependencies and Integration Points

It integrates with VFS ioctl handling, idmapped mounts, inode attribute mutation, ext-family flags, XFS-style fsxattrs, project quotas, DAX, verity, and filesystem-specific fileattr implementations.

## Risks and Edge Cases

Some xflags are read-only or directory-only; mapping them incorrectly can expose unsupported persistence changes. Overlap between flags and xflags must remain consistent. Idmapped mount permission checks affect set operations.

## Test Signals

xfstests for chattr/lsattr, project quota inheritance, DAX/verity flags, idmapped mount permission behavior, unsupported flag rejection, and fsxattr copy_to_user fault handling.
