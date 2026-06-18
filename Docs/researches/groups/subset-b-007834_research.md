# sources/distributed-fs/orangefs/src/client/usrint grouped research: subset-b-007834

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/openfile-util.c -->
# sources/distributed-fs/orangefs/src/client/usrint/openfile-util.c

## Purpose
`openfile-util.c` is the descriptor and initialization core for the OrangeFS/PVFS user-space POSIX interposition layer. It builds the `glibc_ops` dispatch table with real libc entry points, initializes the PVFS client library, and maintains a shared-memory descriptor table that lets intercepted POSIX descriptors refer either to glibc files or PVFS objects through the common `pvfs_descriptor` shape from `posix-ops.h`.

## Important APIs, Types, and Functions
The file-private `pvfs_shmcontrol_t` is the root shared-memory control block. It stores a magic value, process-shared mutex and condition variables, current working directory storage, descriptor table metadata, descriptor and status pools, a path string table, and an inherited descriptor-area fd table. `pvfs_desc_list_t` tracks current and ancestor shared-memory areas after fork/exec so descriptor status can remain shared across related processes. `index_rec_t` implements compact free-list segments for descriptor, status, and path-table allocation.

Public entry points include `load_glibc`, `pvfs_sys_init`, `pvfs_ucache_enabled`, `pvfs_dpath_insert`, `pvfs_dpath_remove`, `pvfs_alloc_descriptor`, `pvfs_dup_descriptor`, `pvfs_find_descriptor`, `pvfs_free_descriptor`, `pvfs_descriptor_table_size`, `pvfs_descriptor_table_next`, `pvfs_put_cwd`, `pvfs_len_cwd`, `pvfs_get_cwd`, `PINT_initrand`, and `PINT_random`. The main internal routines are `init_usrint_internal`, `cleanup_usrint_internal`, `init_descriptor_area_internal`, `init_descriptor_area`, `rebuild_descriptor_table`, `parent_fork_begin`, `parent_fork_end`, `get_desc_table_entry`, and the pool helpers `pvfs_desc_alloc`, `pvfs_desc_free`, `path_index_find`, and `path_index_return`.

## Control Flow
Initialization starts through the constructor `init_usrint_internal` or on demand through `PVFS_INIT(pvfs_sys_init)`. It preserves the caller's `errno`, loads real libc symbols using `dlopen`, `dlsym`, and syscall fallbacks for functions such as `getdents`, seeds the private random state, and then either maps an inherited descriptor table from `PVFS_SHMOBJ` or creates a new one. A fresh process creates a `/dev/shm/pvfs-uid-pid` object, moves it to the magic fd, sizes it from `RLIMIT_NOFILE`, maps it, initializes process-shared synchronization, creates descriptor/status/path/fd pools, records cwd, and allocates descriptors for inherited stdin/stdout/stderr when those fds are live.

Fork handling uses `pthread_atfork`. The parent sets `shmctrl_copy` before fork and waits afterward until the child has copied or shared state. The child duplicates the parent's shared-memory fd, creates its own descriptor area, copies descriptors into the new area, shares PVFS descriptor status objects with the parent where needed, copies glibc descriptor status locally, and signals the parent. Exec recovery maps the inherited area, remaps pointers by stored offsets in `rebuild_descriptor_table`, closes descriptors marked `FD_CLOEXEC`, duplicates the shared-memory object into PVFS true fds, and rebuilds free-list indexes by scanning reachable table entries.

Descriptor allocation always goes through the shared-memory table. `pvfs_alloc_descriptor` reserves a real Linux fd by duplicating the shm object for PVFS files or uses an existing glibc fd, allocates a `pvfs_descriptor` and status, fills fsops, flags, PVFS object reference, file pointer, directory path, and optional user-cache state, and returns with descriptor and status locked for the caller to finish initialization. `pvfs_find_descriptor` lazily wraps unknown live glibc fds, including resolving directory paths from `/proc/self/fd/N`. `pvfs_dup_descriptor` creates descriptor aliases that share the status object and increments `dup_cnt`. `pvfs_free_descriptor` removes the table entry, closes the true fd, applies deferred mode cleanup, releases directory-path storage, closes optional user-cache entries, and returns descriptor/status records to their pools when no duplicates or interprocess shares remain.

## State and Persistence Behavior
Most state lives in a process-shared mmap region: descriptor table pointers, descriptor/status pools, path table bytes, fd-table entries for inherited PDLs, and the user-space cwd string. The shared-memory object is unlinked after mapping so lifetime follows open fds and mappings. PVFS descriptors use duplicated shm-object fds as kernel-visible stand-ins and mark those stand-ins `FD_CLOEXEC`; the user-visible `fdflags` are tracked separately in `pvfs_descriptor`. Descriptor status can survive fork by remaining in an ancestor PDL with reference counts. Cleanup finalizes PVFS, closes PDLs, unmaps the current area, closes the shm fd, and clears globals.

## Dependencies and Integration Points
This file depends on `usrint.h`, `quicklist.h`, `posix-ops.h`, `openfile-util.h`, `iocommon.h`, `posix-pvfs.h`, `pvfs-path.h`, optional `aiocommon.h`, and optional `ucache.h`. It integrates with libc through `glibc_ops`, with the PVFS implementation through `pvfs_ops`, with `iocommon_*` for deferred metadata fixes, with path code for cwd/path storage, and with the POSIX wrappers in `posix.c` that call descriptor lookup and allocation. It also initializes PVFS via `PVFS_util_init_defaults`, silences PVFS perror gossip, and optionally initializes AIO and user cache support.

## Risks and Edge Cases
The shared-memory and pointer-rebuild logic is sensitive to stale offsets, missing locks, and fd inheritance behavior. Several pool helpers log errors but continue after range problems, so corruption can cascade. `path_index_return` and the index rebuild logic rely on zeroed byte runs and string length, which is fragile if a dpath is not null-terminated or is partially overwritten. `add_descriptor_area_list` copies `name_size` bytes without explicitly writing a terminator. `pvfs_find_descriptor` sets `pd->s->mode` from `fstat`, may insert `dpath`, then resets `mode` to zero for implicit glibc descriptors, which can affect later directory/type checks. Some shared-status cleanup logic around `pdl->shares` is hard to reason about and may close a PDL at the wrong reference transition. Initialization exits the process on several descriptor-table failures, which is severe for a preload-style library.

## Test Signals
Useful tests should cover constructor and lazy initialization, glibc fallback calls before and after PVFS init, opening and closing PVFS and non-PVFS files, implicit wrapping of externally opened fds, dup/dup2/dup3/fcntl duplicate semantics, `FD_CLOEXEC` behavior across exec, descriptor sharing after fork, cwd storage across fork, directory `dpath` storage, descriptor-table exhaustion, long path allocation and free-list coalescing, and cleanup/finalize ordering. Stress tests should include concurrent open/close/dup from multiple threads and fork while descriptors are live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/openfile-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/openfile-util.h -->
# sources/distributed-fs/orangefs/src/client/usrint/openfile-util.h

## Purpose
`openfile-util.h` exposes the descriptor-management, initialization, cwd, and path-string helpers implemented by `openfile-util.c` to the rest of the user interface layer. It is the small public contract that lets POSIX wrappers, PVFS operations, stdio support, and path code share the same descriptor table.

## Important APIs, Types, and Functions
The header defines `_P_IO_MAGIC` for PVFS stdio streams, `PVFS_FD_SUCCESS`, `PVFS_FD_FAILURE`, and `PVFS_ATTR_DEFAULT_MASK`, a common stat/getattr mask that includes common metadata, size, block size, symlink target, and directory entry count. It includes `pvfs2-internal.h` and `posix-ops.h`, so exported functions can refer to `PVFS_object_ref`, `posix_ops`, and `pvfs_descriptor`.

Exports include `pvfs_sys_init`, `load_glibc`, `pvfs_ucache_enabled`, path table helpers `pvfs_dpath_insert` and `pvfs_dpath_remove`, lookup/create helpers `pvfs_lookup_dir`, `pvfs_lookup_file`, and `pvfs_create_file`, descriptor helpers `pvfs_alloc_descriptor`, `pvfs_find_descriptor`, `pvfs_dup_descriptor`, `pvfs_free_descriptor`, descriptor table introspection, cwd storage helpers, and private-random helpers `PINT_initrand` and `PINT_random`.

## Control Flow
Callers typically use `PVFS_INIT(pvfs_sys_init)` before touching descriptors. Path and open routines call `pvfs_alloc_descriptor` after a real glibc fd or PVFS object has been opened, retain the returned locked descriptor until they finish setting flags/mode/path fields, and later use `pvfs_find_descriptor` for dispatch. Close, dup, cwd, and stdio code call the smaller helpers directly.

## State and Persistence Behavior
The header does not own state, but every descriptor and cwd helper refers to the shared-memory state in `openfile-util.c`. `PVFS_ATTR_DEFAULT_MASK` affects metadata fetched from PVFS servers and is reused in close-time deferred mode handling and stat implementations.

## Dependencies and Integration Points
This header bridges `posix.c`, `posix-pvfs.c`, `pvfs-path.c`, `overunder.c`, stdio support, and iocommon code. It assumes `posix_ops` and `pvfs_descriptor` are available from `posix-ops.h`, and it exposes functions implemented partly in other compilation units (`pvfs_lookup_dir`, `pvfs_lookup_file`, `pvfs_create_file` are declared here but not implemented in `openfile-util.c`).

## Risks and Edge Cases
The broad include surface means changes to `posix_ops` or `pvfs_descriptor` ripple through most usrint files. The declared lookup/create helpers need implementation consistency elsewhere. The default attribute mask is duplicated in `posix-pvfs.c`, so mask changes can diverge.

## Test Signals
Build tests should verify all declarations match definitions under feature flags such as user cache, AIO, and 64-bit redirects. Runtime tests should exercise descriptor allocation, lookup, duplication, free, cwd get/put, and metadata calls that rely on `PVFS_ATTR_DEFAULT_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/openfile-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/overunder.c -->
# sources/distributed-fs/orangefs/src/client/usrint/overunder.c

## Purpose
`overunder.c` implements glibc libio underflow, uflow, and overflow hooks for PVFS-backed `FILE` streams. It lets the user-space interface fill and flush stdio buffers through PVFS stream helpers while rejecting non-PVFS streams.

## Important APIs, Types, and Functions
The file exports `__underflow(FILE *stream)`, `__uflow(FILE *stream)`, and `__overflow(FILE *stream, int ch)`. It depends on old glibc libio layout definitions in `old_libio.h`, stream operation helpers from `stdio-ops.h`, and `_P_IO_MAGIC` from `openfile-util.h`. Helper macros such as `ISMAGICSET` and `ISFLAGSET` check the stream magic and flags, while `pvfs_set_to_get`, `pvfs_set_to_put`, `pvfs_read_buf`, and `pvfs_write_buf` do the actual stream state transitions and I/O.

## Control Flow
Both read hooks first validate that the stream exists and has `_P_IO_MAGIC`. If it is a normal glibc `_IO_MAGIC` stream, comments indicate that the correct behavior would be to delegate to glibc, but that delegation is not implemented here. If the stream is in put mode, they switch it to get mode. If buffered read data is already available, `__underflow` returns the next byte without advancing and `__uflow` returns it while advancing `_IO_read_ptr`. Otherwise they refill with `pvfs_read_buf` and return EOF on no bytes.

`__overflow` validates the PVFS stream, switches into put mode if necessary, flushes the write buffer when already putting, writes `ch` at `_IO_write_ptr`, advances the pointer, and returns the character or EOF on flush failure.

## State and Persistence Behavior
The file mutates glibc-style `FILE` internals: read pointers, write pointers, and mode flags. Persistent file state is in the stream object and, indirectly, in the PVFS descriptor behind the stream. There is no explicit locking in this file, so safety depends on surrounding stdio locking or caller discipline.

## Dependencies and Integration Points
This code integrates with the usrint stdio implementation, `openfile-util.c` for the PVFS stream magic, and the low-level POSIX/PVFS read/write path used by `stdio-ops`. It also detects glibc streams but currently returns `EINVAL` rather than forwarding to glibc hooks.

## Risks and Edge Cases
The lack of delegation for `_IO_MAGIC` streams can break mixed PVFS/glibc stdio if these symbols interpose globally. `__overflow` writes `ch` after flushing but does not visibly check whether space is available in the buffer after the mode switch or flush. EOF and error handling are minimal. Direct reliance on old libio internals is version-sensitive.

## Test Signals
Tests should cover `fgetc` lookahead vs consuming behavior, refill at buffer boundary, EOF propagation, switching from write to read and read to write, write-buffer flush failures, invalid/null streams, normal glibc stream behavior under interposition, and compatibility across supported glibc versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/overunder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-ops.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.c -->
# sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.c

## Purpose
`posix-pvfs.c` implements the PVFS side of the `posix_ops` dispatch table. It translates POSIX-like operations into OrangeFS/PVFS client calls, mostly through `iocommon_*`, while preserving user-space descriptor state such as file offsets, duplicate semantics, umask, cwd, and fallback behavior when a symlink resolves out of PVFS.

## Important APIs, Types, and Functions
The file exports helper APIs `pvfs_valid_path`, `pvfs_valid_fd`, `pvfs_layout`, `pvfs_layout_fd`, `pvfs_layout_string`, and `pvfs_release_layout`. It implements open/create/delete/rename (`pvfs_open`, `pvfs_openat`, `pvfs_unlink`, `pvfs_rename`, etc.), I/O (`pvfs_read`, `pvfs_write`, `pvfs_readv`, `pvfs_writev`, `pvfs_prdwr64`, `pvfs_rdwrv`), seek/truncate/sync, stat and statfs families, time/owner/mode mutations, directory and symlink operations, xattrs and atomic xattrs, cwd and umask helpers, SELinux stubs, and finally the `posix_ops pvfs_ops` initializer.

`mask_val` stores the PVFS-layer umask. `PVFS_ATTR_DEFAULT_MASK` is duplicated locally. Layout helpers build `PVFS_sys_layout` structures from a path or fd and an ASCII server list, using `iocommon_parse_serverlist` and `BMI_addr_rev_lookup`.

## Control Flow
Path-based operations usually qualify or expand the path with `PVFS_qualify_path` or `PVFS_expand_path`, then call `iocommon_open` to obtain a descriptor or call an iocommon metadata function directly. If an opened object resolves to `glibc_ops`, several operations fall back to glibc f* calls on `pd->true_fd`. Relative `*at` operations validate the directory descriptor with `pvfs_find_descriptor` and pass `pd->s->pvfs_ref` as a parent reference.

I/O operations look up the descriptor, validate access mode against `O_ACCMODE`, wrap scalar buffers as an iovec when needed, and call `iocommon_readorwrite`. Sequential read/write and vector I/O update `pd->s->file_pointer`; append writes stat the file first and write at current size. `pvfs_lseek64` delegates pointer update to `iocommon_lseek`. `pvfs_dup`, `pvfs_dup2`, `pvfs_dup3`, and `pvfs_fcntl(F_DUPFD)` all use `pvfs_dup_descriptor`.

Metadata calls often open the target read-only, call `iocommon_stat`, `iocommon_chown`, `iocommon_chmod`, `iocommon_setattr`, `iocommon_statfs`, or xattr helpers, then close the temporary descriptor. `pvfs_close` frees descriptor state and optionally applies `clrflags` mode cleanup. `pvfs_sync` is a no-op; `pvfs_fsync` calls `iocommon_fsync` for PVFS descriptors and skips glibc fallback descriptors. SELinux label calls uniformly return `ENOTSUP`.

## State and Persistence Behavior
Per-open state is in `pvfs_descriptor_status`: file pointer, flags, mode, directory token, dpath, PVFS object reference, and optional cache entry. `posix-pvfs.c` mutates file pointer and flags and relies on `openfile-util.c` for descriptor lifetime. Persistent filesystem state changes are made through iocommon calls to PVFS servers: creates, unlinks, renames, truncates, setattr for times/ownership/mode, xattrs, directory creation, symlink creation, and fsync. The PVFS cwd is stored in the shared descriptor control area through `pvfs_put_cwd` and retrieved by `pvfs_getcwd` helpers.

## Dependencies and Integration Points
The implementation depends on `posix-ops.h`, `posix-pvfs.h`, `openfile-util.h`, `iocommon.h`, `pvfs-path.h`, and BMI. It is called by `posix.c` through the `pvfs_ops` table and directly by external code via `posix-pvfs.h`. It uses `glibc_ops` for fallback and libc-compatible behavior. The layout helpers integrate with server address parsing and reverse lookup through `iocommon_parse_serverlist` and BMI.

## Risks and Edge Cases
Several operations return approximate semantics: `pvfs_fallocate` truncates to `offset + length`, `pvfs_fdatasync` is the same as fsync, `pvfs_sync` does nothing, nanosecond timestamps are truncated to seconds, fadvise validates advice but does nothing, hard links and flock are `ENOSYS`, and SELinux labels are `ENOTSUP`. `pvfs_mknodat` switches on `dev` rather than the file-type bits in `mode`, which looks inconsistent with POSIX `mknod`. `pvfs_futimes` closes the fd it was asked to update, which is surprising for an f* API. Some absolute-path branches do not always qualify paths before iocommon calls. The `pvfs_ops` table maps `statfs` and `statvfs` to the interposed `statfs`/`statvfs` symbols instead of `pvfs_statfs`/`pvfs_statvfs`, explicitly marked "probably special" and worth testing for recursion or dispatch surprises.

## Test Signals
Tests should cover PVFS open/openat with absolute and relative paths, O_CREAT mode and hints, symlink-to-glibc fallback, sequential and positioned I/O offsets, O_APPEND, readv/writev offset updates, lseek boundaries, truncate/ftruncate/fallocate behavior, close without unwanted fsync, stat/lstat/fstatat variants, futimes/futimens preservation of fds, chmod/chown nofollow handling, mkdir/rmdir/unlinkat flags, readlink/symlink, unimplemented link/flock errors, xattr and atomic xattr round trips, statfs/statvfs dispatch, cwd helpers, umask masking, and the final `pvfs_ops` table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix.c -->
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
Several `*at` wrappers call a helper but do not assign its return value in the `AT_FDCWD` or absolute-path branch, including patterns like `utimes(path, times);`, `chown(path, owner, group);`, `chmod(path, mode);`, `mkdir(path, mode);`, `readlink(path, buf, bufsiz);`, `symlink(oldpath, newpath);`, `access(path, mode);`, and `mknod(path, mode, dev);`. Those branches may return the initial `rc` value rather than the real result. `writev` dispatches with `fd` instead of `pd->true_fd`, unlike most other fd wrappers, which is risky for PVFS stand-in fds. `lseek` treats any high 32 bits in the 64-bit result as an `EFAULT`, which can reject valid large offsets for signed/off_t configurations. `renameat` and `linkat` do not handle `AT_FDCWD` specially before `pvfs_find_descriptor`, so common POSIX cases can fail with `EBADF`. Mixed PVFS and non-PVFS path handling depends on correct path expansion and freeing.

## Test Signals
Tests should preload/interpose this library and exercise each wrapper on PVFS and non-PVFS paths. Priority cases are non-PVFS open followed by read/write/close, PVFS open and descriptor dispatch, null pointer errors, all `*at` wrappers with `AT_FDCWD`, absolute paths and relative dirfds, rename/link cross-fs `EXDEV`, stat alias functions, xattr availability when libc lacks xattr symbols, large lseek offsets, writev on PVFS fds, and path freeing under success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/pvfs-path.c -->
# sources/distributed-fs/orangefs/src/client/usrint/pvfs-path.c

## Purpose
`pvfs-path.c` decides whether a pathname belongs to PVFS and expands/qualifies paths for the user-space interface. It resolves relative paths, dot and dot-dot components, symlinks, mount points, and final filename splits while preserving metadata in `PVFS_path_t`.

## Important APIs, Types, and Functions
The public functions are `PVFS_expand_path(const char *path, int skip_last_lookup)`, `is_pvfs_path(const char **path, int skip_last_lookup)`, and `split_pathname(const char *path, char **directory, char **filename)`. `PVFS_expand_path` operates on `PVFS_path_t` objects from helpers such as `PVFS_path_from_expanded`, `PVFS_new_path`, `PVFS_qualify_path`, and `PVFS_free_expanded`. It sets and clears flags such as `PATH_EXPANDED`, `PATH_RESOLVED`, `PATH_LOOKEDUP`, `PATH_MNTPOINT`, and `PATH_ERROR`, and fills `fs_id`, `handle`, `pvfs_path`, and `filename` fields as lookup progresses.

## Control Flow
`PVFS_expand_path` starts from an existing expanded PVFS path object or creates a new one. Relative paths are prefixed with `getcwd`; absolute paths start at `/`. It loops over components, skipping repeated slashes and `.`, backing up for `..`, checking length, resolving mount points with `PVFS_util_resolve_absolute`, optionally skipping final lookup for lstat/readlink-style no-follow behavior, and looking up PVFS components with `iocommon_lookup_absolute(PVFS2_LOOKUP_LINK_NO_FOLLOW)`. If a PVFS component is a symlink, it gets `PVFS_ATTR_SYS_LNK_TARGET` and restarts or rewrites the remaining path. For non-PVFS components, it uses raw syscalls `SYS_readlink` and `SYS_stat` to avoid interposition loops. A 16-link limit prevents infinite symlink expansion.

`is_pvfs_path` initializes the library, validates input, and either uses kernel-mount detection under `PVFS_USRINT_KMOUNT` with glibc `stat/statfs`, or creates a `PVFS_path_t`, qualifies it, resolves it through PVFS mount tables, and if necessary calls `PVFS_expand_path`. It rewrites `*path` to the expanded path and returns 1 for PVFS, 0 otherwise. `split_pathname` allocates directory and filename pieces from a clean path and treats root-level and trailing-slash cases as errors with `EISDIR` or `ENOENT`.

## State and Persistence Behavior
Path state is held in allocated `PVFS_path_t` objects and their embedded original/expanded strings. The function updates object flags, return code, fs id, handle, filename pointer, and path pointers. It may allocate temporary symlink-rewrite buffers while expanding. Callers that receive an expanded path are responsible for `PVFS_free_expanded` where appropriate. No filesystem state is changed except lookups and stats.

## Dependencies and Integration Points
The file depends on `usrint.h`, `openfile-util.h`, `iocommon.h`, and `pvfs-path.h`. It integrates directly with `posix.c` path dispatch, `posix-pvfs.c` qualification and cwd behavior, PVFS mount resolution through `PVFS_util_resolve_absolute`, iocommon lookup/getattr, and glibc/syscall fallback for non-PVFS path components. It also calls `pvfs_sys_init`, so path checks can trigger full usrint initialization.

## Risks and Edge Cases
Path expansion is subtle around `skip_last_lookup`; the code has a suspicious check for `*p == '.' && *(p+1) == '0'`, likely intended for `.` followed by NUL. `PVFS_expand_path` sets `PATH_ERROR` only if `Ppath->rc != 0`, but local `ret` errors may not always propagate into `Ppath->rc`. In the kernel-mount branch, `strnlen(path, PVFS_PATH_MAX)` appears to use the pointer-to-pointer rather than `*path`, which would be wrong if compiled. `split_pathname` assigns `filename = NULL` instead of `*filename = NULL` in one trailing-slash branch. The path logic depends on correct ownership and lifetime of `PVFS_path_t` buffers, and incorrect freeing can affect every wrapper.

## Test Signals
Tests should cover absolute and relative paths, cwd in PVFS and non-PVFS locations, repeated slashes, dot and dot-dot normalization, PVFS and non-PVFS symlinks, absolute and relative symlink targets, symlink loops over 16 expansions, missing final components for create, lstat/readlink no-follow behavior, mount point detection, paths crossing from PVFS to non-PVFS, very long paths, root-level paths, trailing slashes, and memory ownership with `PVFS_free_expanded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/usrint/pvfs-path.c -->
