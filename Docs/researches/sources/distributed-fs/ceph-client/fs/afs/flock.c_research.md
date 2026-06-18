# sources/distributed-fs/ceph-client/fs/afs/flock.c

Purpose: `flock.c` implements POSIX locks and BSD flock emulation over AFS whole-file, time-limited server locks, combining local VFS locks with server acquisition, extension, release, and callback-driven retry.

Important APIs and functions: exported entry points are `afs_lock()`, `afs_flock()`, `afs_lock_may_be_available()`, `afs_lock_op_done()`, and `afs_lock_work()`. Key helpers include `afs_set_lock()`, `afs_extend_lock()`, `afs_release_lock()`, `afs_next_locker()`, `afs_grant_locks()`, `afs_defer_unlock()`, `afs_do_setlk()`, `afs_do_unlk()`, and `afs_do_getlk()`.

Control flow: set-lock validates vnode status and permissions, maps partial-lock behavior through configured flock mode, optionally skips server locking for local/OpenAFS-compatible partial locks, queues a pending lock, reuses compatible server locks when possible, otherwise issues SetLock and waits/retries on contention. The VFS lock manager still arbitrates local byte ranges after the server lock is obtained. Delayed work extends leases, retries waiters, and releases server locks when the local granted list empties.

State and persistence: vnode lock state includes `lock_state`, `lock_type`, `lock_key`, `locked_at`, `pending_locks`, `granted_locks`, and delayed `lock_work`. Individual `file_lock` objects carry AFS state and debug IDs. Deleted vnodes wake waiters with `-ENOENT`.

Dependencies and integration points: VFS lock APIs, `fs_operation.c`, lock RPCs in `fsclient.c`, callback breaks, permission checks, server `lock_count`, `afs_lock_manager`, and tracing. Registered by `file.c`.

Risks: local reuse of server locks can starve other clients. Signals after server dispatch can leave a lock until expiry. Workqueue release/extension failures must not wedge local state. Partial-lock semantics vary by mode.

Test signals: read/write locks, partial locks in all modes, nonblocking contention, callback retry, extension failure, unlock while extending, vnode deletion with waiters, VFS rejection after server lock, `GETLK`, and flock validation.
