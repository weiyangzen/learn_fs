# sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.h

## Purpose
`posix-pvfs.h` declares the PVFS-specific POSIX-compatible API implemented in `posix-pvfs.c`. It is the external and internal prototype surface for callers that want to invoke PVFS operations directly rather than through interposed libc symbols.

## Important APIs, Types, and Functions
The header defines `PVFS_FD_NOCACHE`, a PVFS-only fd flag. It declares layout helpers, path/fd validity checks, all open/create/delete/rename operations, read/write variants, seek/truncate/fallocate/close/flush, stat and lstat variants with mask helpers, timestamp calls, dup calls, ownership and permission calls, directory/symlink/link operations, getdents and access, flock/fcntl/sync/fadvise, statfs/statvfs, mknod/sendfile, xattrs plus OrangeFS atomic xattrs, cwd and umask helpers, mmap/msync declarations, optional ACL prototypes, and SELinux label stubs.

## Control Flow
`posix.c` chooses PVFS vs glibc for path-based operations using `is_pvfs_path`, then calls these functions for PVFS paths. Descriptor-based wrappers dispatch through `pvfs_ops`, whose entries correspond to these prototypes. External users can also include this header to call PVFS operations directly.

## State and Persistence Behavior
The header does not store state but exposes operations that mutate descriptor state, PVFS metadata, cwd, umask, xattrs, and filesystem data. The prototypes imply that callers must manage returned layout objects with `pvfs_release_layout` and must treat fd-based APIs as operating through the usrint descriptor table.

## Dependencies and Integration Points
The declarations depend on PVFS types such as `PVFS_sys_layout`, POSIX types such as `struct stat`, `struct statfs`, `struct statvfs`, `struct iovec`, xattr buffers, and optional ACL/SELinux types. It integrates with `posix-ops.h` through `pvfs_ops`, with `openfile-util.h` for descriptor state, and with `pvfs-path.c` for path validity.

## Risks and Edge Cases
The API is broad and mirrors libc, so signature drift from libc or `posix_ops` can cause subtle ABI mismatches. Several declared functions are stubs or approximations in the implementation. `pvfs_flush` and mmap functions are declared here but not defined in the researched `posix-pvfs.c` segment, so they must be supplied by other usrint files or will fail at link time under relevant builds.

## Test Signals
Build tests should compare declarations against implementation and `pvfs_ops` initializers. Runtime coverage should exercise direct calls and interposed calls for representative path, fd, metadata, xattr, cwd, and unsupported-operation cases.
