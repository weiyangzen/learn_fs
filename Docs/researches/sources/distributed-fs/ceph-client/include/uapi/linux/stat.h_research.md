# sources/distributed-fs/ceph-client/include/uapi/linux/stat.h

## Purpose
Provides file type, permission, and `statx()` UAPI definitions. It lets userspace request and interpret extended file metadata such as birth time, mount IDs, direct-I/O alignment, subvolume ID, and atomic write properties.

## Important APIs, Types, and Constants
Classic mode constants include `S_IFMT`, `S_IFSOCK`, `S_IFLNK`, `S_IFREG`, `S_IFBLK`, `S_IFDIR`, `S_IFCHR`, `S_IFIFO`, `S_ISUID`, `S_ISGID`, `S_ISVTX`, `S_IS*()` predicates, and permission bits. `struct statx_timestamp` and `struct statx` define the `statx()` result layout. Request/result masks include `STATX_TYPE`, `STATX_MODE`, `STATX_BASIC_STATS`, `STATX_BTIME`, `STATX_MNT_ID`, `STATX_DIOALIGN`, `STATX_MNT_ID_UNIQUE`, `STATX_SUBVOL`, `STATX_WRITE_ATOMIC`, and `STATX_DIO_READ_ALIGN`. Attribute flags include compressed, immutable, append-only, encrypted, automount, mount-root, verity, DAX, and atomic-write support.

## Control Flow, State, and Persistence
The file is ABI structure only. Kernel filesystems fill `struct statx` based on requested masks and available metadata. Unsupported fields are cleared or fabricated for compatibility.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `statx(2)`, VFS, distributed filesystems such as Ceph, libc wrappers, backup tools, and file managers.

## Risks and Test Signals
Risks include struct layout drift, mask/attribute confusion, reserved bit misuse, and filesystem-specific partial support. Test with compile-time size/offset checks, `statx()` mask combinations, filesystem matrix tests, direct-I/O alignment validation, and 32-bit userspace compatibility.
