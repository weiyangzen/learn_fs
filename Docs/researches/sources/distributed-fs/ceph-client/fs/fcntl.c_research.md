# sources/distributed-fs/ceph-client/fs/fcntl.c

## Purpose
`fcntl.c` implements the Linux `fcntl` and compat `fcntl` syscalls, file flag changes, file ownership for SIGIO/SIGURG, write-life hints, descriptor duplication queries, leases/delegations dispatch, pipe/memfd fcntls, and fasync registration/signal delivery. It is generic VFS/syscall infrastructure used by all filesystems and device drivers.

## Important APIs, Types, and Functions
- `setfl()` applies `F_SETFL` changes for append, nonblocking, direct IO, noatime, and fasync flags.
- `file_f_owner_allocate()`, `__f_setown()`, `f_setown()`, `f_getown()`, `f_setown_ex()`, and `f_getown_ex()` manage `struct fown_struct`.
- `do_fcntl()` dispatches most native fcntl commands.
- `SYSCALL_DEFINE3(fcntl)` and 32-bit `fcntl64` perform fd lookup, `FMODE_PATH` restrictions, LSM checks, and dispatch.
- Compat helpers translate `struct flock` layouts and command values.
- `send_sigio()`, `send_sigurg()`, `fasync_helper()`, `fasync_insert_entry()`, `fasync_remove_entry()`, and `kill_fasync()` implement asynchronous notification.
- `fcntl_init()` creates the `fasync_cache` and validates open flag bit uniqueness.

## Control Flow
The syscall path obtains the file from the fd table, rejects most commands on `FMODE_PATH`, calls `security_file_fcntl()`, then dispatches. `do_fcntl()` handles descriptor flags, file flags, file locks, owner/signal configuration, leases, dnotify, pipe sizing, memfd seals, write-life hints, delegations, and created/dup queries.

`F_SETFL` goes through `setfl()`: it enforces append-only and noatime permissions, normalizes `O_NDELAY`, validates `O_DIRECT`, delegates filesystem/device-specific flag checks, updates fasync registration if requested, and finally updates `f_flags` under `filp->f_lock`.

Async notification stores target pid/pid_type and credentials in `fown_struct`. Signal delivery checks credentials and LSM permission, queues realtime signal info for configured signals, falls back to SIGIO, and supports process-group fanout. Fasync lists are protected by `fasync_lock`, per-file `f_lock`, per-entry `fa_lock`, and RCU for safe traversal during `kill_fasync()`.

## State and Persistence
State is in-memory kernel state: `file->f_flags`, `file->f_iocb_flags`, close-on-exec fd bits, `file->f_owner`, inode write-life hints, fasync lists, and lock/lease/delegation state owned by other subsystems. No filesystem media is directly persisted here, though write hints and locks affect later IO behavior.

## Dependencies and Integration Points
The file integrates with fdtable helpers, VFS file locking, leases, dnotify, pipefs, memfd, LSM hooks, pid namespaces, credentials, signals, RCU, slab caches, user copy helpers, and compat syscall ABI. Filesystems and drivers integrate by implementing `file_operations::check_flags` and `::fasync`, and by using `kill_fasync()` to notify listeners.

## Risks and Test Signals
`F_GETOWN` can return negative process-group IDs and therefore uses `force_successful_syscall_return()`. Owner allocation is race-safe through `cmpxchg`. `O_APPEND` cannot be cleared on append-only files, and `O_NOATIME` requires ownership/capability. Compat lock structures need overflow fixups. Tests should cover descriptor flags, `F_SETFL` permission failures, fasync registration/removal, SIGIO/SIGURG delivery, compat/OFD locks, pipe sizing, memfd seals, write-life hints, `FMODE_PATH` restrictions, and LSM denial paths.
