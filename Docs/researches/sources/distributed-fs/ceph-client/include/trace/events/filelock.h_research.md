<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filelock.h -->
# sources/distributed-fs/ceph-client/include/trace/events/filelock.h

## Purpose
Defines VFS file lock and lease tracepoints for POSIX locks, flock locks, open-file-description locks, leases, and lease conflict/break handling.

## APIs, Control Flow, and State
Format helpers decode `FL_*` flags and `F_RDLCK`/`F_WRLCK`/`F_UNLCK` types. `locks_get_lock_context` reports inode device/number, requested type, and lock context pointer. The `filelock_lock` class is instantiated as `posix_lock_inode`, `fcntl_setlk`, `locks_remove_posix`, and `flock_lock_inode`; it records lock pointer, blocker, owner, pid, flags, type, byte range, inode identity, and return code. The `filelock_lease` class is instantiated for lease break/delete/timeouts and records lease pointer, blocker, owner, flags, type, break time, and downgrade time. `generic_add_lease` captures inode read/write/open counts when adding a lease, and `leases_conflict` records both lease and breaker attributes plus conflict result. No lock state is owned here; the header snapshots `struct file_lock`, `struct file_lease`, inode counters, and contexts.

## Dependencies, Integration, Risks, and Tests
Depends on VFS inode/file-lock structures, device number helpers, atomic inode counters, and tracepoints. Integration points are `fcntl(F_SETLK*)`, flock, OFD locks, NFS/cluster lock layers using VFS helpers, lease acquisition/break, and lock context allocation. Risks include null lock handling differences across events, exposing owner pointers, stale pointer reuse after lock teardown, and interpreting byte ranges without knowing mandatory/advisory context. Test signals include locktests for POSIX/flock/OFD locks, blocking conflict scenarios, lease break and timeout tests, NFS lock integration, and tracing error returns for nonblocking locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filelock.h -->
