# sources/distributed-fs/ceph-client/include/uapi/linux/fcntl.h

This UAPI header layers Linux-specific `fcntl` commands and `*at` syscall flags on top of architecture `asm/fcntl.h`. It defines leases, dnotify, fd duplication queries, pipe sizing, memfd seals, write lifetime hints, delegations, special dirfd constants, pidfs/nsfs root constants, and path-operation flags.

Important exports include `F_SETLEASE`, `F_GETLEASE`, `F_NOTIFY`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `F_DUPFD_CLOEXEC`, `F_SETPIPE_SZ`, `F_GETPIPE_SZ`, `F_ADD_SEALS`, `F_GET_SEALS`, seal flags `F_SEAL_*`, write lifetime hint commands and `RWH_WRITE_LIFE_*`, delegation commands and `struct delegation`, dnotify `DN_*` masks, `AT_FDCWD`, `PIDFD_SELF_THREAD`, `PIDFD_SELF_THREAD_GROUP`, `FD_PIDFS_ROOT`, `FD_NSFS_ROOT`, `FD_INVALID`, generic `AT_*` flags, rename/access/unlink/handle flags, and `AT_EXECVE_CHECK`.

Control flow is syscall argument interpretation: `fcntl` dispatches commands against an fd, while openat/statx/unlinkat/renameat2/name_to_handle_at/execveat-style syscalls interpret `AT_*` flags against dirfd and path arguments. State includes file locks/leases, dnotify registrations, pipe buffer sizes, inode or file write-hint metadata, memfd seal masks, and filesystem namespace resolution. Persistence varies: seals persist for memfd lifetime, write hints may live on inode or open file, and path flags affect only one syscall.

Dependencies include `asm/fcntl.h`, `linux/openat2.h`, `linux/types.h`, VFS lock/lease/seal code, pipe implementation, pidfs/nsfs, and path resolution. Integration points include libc, coreutils, memfd users, container runtimes, pidfd-aware tools, NFS/delegation users, and statx/openat2 security patterns.

Risks include overlapping per-syscall flag values, fd leaks when CLOEXEC is omitted, seal semantics mistakes that allow writes/exec changes after sealing, ambiguous PID/thread special fd constants, and ABI collisions with architecture-specific `fcntl` bases. Test signals include fcntl syscall selftests, memfd seal tests, pipe sizing tests, path resolution flag tests, pidfd special constant tests, delegation/lease tests, and cross-architecture header checks.
