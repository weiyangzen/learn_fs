# sources/distributed-fs/orangefs/src/client/usrint/posix-ops.h

## Purpose
`posix-ops.h` defines the dispatch abstraction used by the usrint layer. A `posix_ops` table holds function pointers for POSIX-like file, directory, metadata, xattr, socket, mmap, and SELinux operations. Each `pvfs_descriptor_status` carries a pointer to either `glibc_ops` or `pvfs_ops`, allowing wrapper functions to dispatch per descriptor.

## Important APIs, Types, and Functions
The central type is `struct posix_ops_s`, aliased as `posix_ops`. It includes file open/create/delete/rename, read/write variants, seek/truncate/close/stat variants, time, ownership, permissions, directory, symlink/link, getdents, access, lock/fcntl, sync, filesystem stats, mknod, sendfile, extended attributes, socket operations, umask/getdtablesize, mmap/munmap/msync, and SELinux label operations. `glibc_ops` and `pvfs_ops` are declared as the two concrete dispatch tables.

The header also defines `pvfs_mmap_t`, `pvfs_descriptor_status`, and `pvfs_descriptor`. `pvfs_descriptor_status` contains shared open-file state: lock, duplicate count, dispatch table, PVFS object reference, open flags, clear-on-close mode bits, mode, deferred mode changes, file pointer, directory iteration token, directory path for `fchdir`, and optional user-cache file entry. `pvfs_descriptor` contains per-fd state: lock, in-use marker, public fd, true fd, fd flags, shared-status flag, and status pointer. `PFILE` and `PDIR` alias `pvfs_descriptor`.

## Control Flow
`openfile-util.c` creates and populates descriptors and status objects. `posix.c` looks up a descriptor for each intercepted libc symbol and calls the function pointer in `pd->s->fsops`. `posix-pvfs.c` initializes `pvfs_ops` with PVFS implementations, while `openfile-util.c` fills `glibc_ops` dynamically with libc symbols. Duplicate descriptors share `pvfs_descriptor_status`, so file pointer and open flags follow POSIX open-file-description semantics.

## State and Persistence Behavior
This header defines the memory layout that is stored in shared memory across fork and exec. Any field ordering or type change affects pointer rebuild, shared descriptor status, and compatibility with existing mapped descriptor areas. `pvfs_descriptor_status` is intentionally shared among duped descriptors and sometimes across processes; `pvfs_descriptor` remains unique to a descriptor slot.

## Dependencies and Integration Points
The header assumes many system types are already visible through `usrint.h` or callers, including `struct stat`, `struct statfs`, `struct statvfs`, `struct iovec`, `struct dirent`, `PVFS_object_ref`, `PVFS_ds_position`, `gen_mutex_t`, and `struct qlist_head`. It integrates with `openfile-util.h`, `posix.c`, `posix-pvfs.c`, mmap support, optional ACL code, xattr support, and SELinux stub or libc functions.

## Risks and Edge Cases
Because the function table is very wide, missing initialization of a function pointer can surface as a null call in wrappers. The `BITDEFS` macro remaps some names to 64-bit variants, so build configuration can change ABI assumptions. Several function pointer signatures use nonstandard or typo-prone names, and socket operations are carried in the same table even though PVFS does not implement them. Shared-memory layout changes are high risk.

## Test Signals
Compile-time tests should validate that `glibc_ops` and `pvfs_ops` initializers cover required fields under all feature flags. Runtime tests should dispatch the same operation through glibc and PVFS descriptors, duplicate descriptors and verify shared file offset, verify fd flags vs status flags, and exercise xattr/statfs/mmap function pointers when compiled in.
