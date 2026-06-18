# sources/distributed-fs/orangefs/src/client/usrint/posix.c

## Purpose
`posix.c` provides the libc-symbol interposition layer for OrangeFS/PVFS user-space I/O. It defines wrappers named like POSIX and glibc entry points, chooses PVFS or glibc based on path resolution or descriptor metadata, and dispatches to `pvfs_ops` or `glibc_ops`.

## Important APIs, Types, and Functions
The file exports wrappers for `open`, `open64`, `openat`, `creat`, `unlink`, `rename`, read/write variants, lseek, truncate, close, stat and glibc xstat aliases, fstatat/lstat variants, time calls, dup calls, ownership/mode/directory/symlink/link calls, getdents, access, flock/fcntl, sync/fsync/fdatasync/fadvise, statfs/statvfs, mknod, sendfile, xattrs, and optional cwd/umask/getdtablesize wrappers under `PVFS_USRINT_CWD`. It declares Linux-only prototypes for `getdents`, `getdents64`, `flock`, and `fadvise64`.

## Control Flow
Path-based wrappers validate pointers, call `is_pvfs_path(&path, skip_last_lookup)`, then dispatch to a PVFS function for PVFS paths or to the real libc function through `glibc_ops` for non-PVFS paths. `open_internal` also allocates a descriptor for non-PVFS files after glibc open so later descriptor-based wrappers can dispatch through the descriptor table. It stores mode, flags, and directory path when applicable, then frees the expanded path with `PVFS_free_expanded`.

Descriptor-based wrappers call `pvfs_find_descriptor(fd)` and then invoke `pd->s->fsops->operation(pd->true_fd, ...)`. That makes descriptors opened through glibc use `glibc_ops` and descriptors opened through PVFS use `pvfs_ops`. `*at` wrappers either treat `AT_FDCWD` and absolute paths as ordinary path operations or look up the directory fd and dispatch through that descriptor's fsops. Rename/link variants reject cross-filesystem operations with `EXDEV` when the two sides resolve to different fsops.

## State and Persistence Behavior
The wrapper layer primarily mutates descriptor state indirectly. Non-PVFS opens create `glibc_ops` descriptors in the shared descriptor table; PVFS opens are allocated by `pvfs_open`. Reads, writes, seeks, fcntl, dup, and close mutate the descriptor table or shared status through the selected fsops. The wrappers themselves allocate expanded path objects and must free them after dispatch.

## Dependencies and Integration Points
This file depends on `usrint.h`, `posix-ops.h`, `posix-pvfs.h`, `openfile-util.h`, and `pvfs-path.h`. It is the consumer of `glibc_ops` loaded by `openfile-util.c` and `pvfs_ops` initialized by `posix-pvfs.c`. It also exposes glibc ABI aliases such as `__xstat`, `__fxstat`, and `__lxstat` so older glibc stat calls route through the same logic.

## Risks and Edge Cases
Several `*at` wrappers call a helper but do not assign its return value in the `AT_FDCWD` or absolute-path branch, including patterns like `utimes(path, times);`, `chown(path, owner, group);`, `chmod(path, mode);`, `mkdir(path, mode);`, `readlink(path, buf, bufsiz);`, `symlink(oldpath, newpath);`, `access(path, mode);`, and `mknod(path, mode, dev);`. Those branches may return the initial `rc` value rather than the real result. `writev` dispatches with `fd` instead of `pd->true_fd`, unlike most other fd wrappers. `lseek` treats any high 32 bits in the 64-bit result as an error. `renameat` and `linkat` do not handle `AT_FDCWD` specially before descriptor lookup.

## Test Signals
Tests should preload/interpose this library and exercise each wrapper on PVFS and non-PVFS paths. Priority cases are non-PVFS open followed by read/write/close, PVFS open and descriptor dispatch, null pointer errors, all `*at` wrappers with `AT_FDCWD`, absolute paths and relative dirfds, rename/link cross-fs `EXDEV`, stat alias functions, xattr availability when libc lacks xattr symbols, large lseek offsets, writev on PVFS fds, and path freeing under success and failure.
