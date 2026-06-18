# sources/distributed-fs/openafs/src/rx/NBSD/rx_kmutex.h

Purpose: NetBSD Rx locking abstraction for both modern NetBSD 5+ and older lockmgr/simplelock systems.

Important APIs/types/functions: NetBSD 5+ maps `afs_kmutex_t` to `kmutex_t` and `afs_kcondvar_t` to `kcondvar_t`; older path defines a struct lock plus owner `lwp`; macros `MUTEX_*`, `CV_*`, `CV_WAIT`, and `CV_WAIT_SIG`.

Control flow: modern path delegates waits to `afs_cv_wait`; older path manually drops AFS global lock, exits the mutex, sleeps with `ltsleep` using a local simplelock, then reacquires both.

State/persistence: per-lock kernel mutex or lockmgr state, owner tracking in older path.

Dependencies/integration: NetBSD kernel locking headers, OpenAFS global lock, and optional `LOCKDEBUG`.

Risks: older `CV_WAIT` uses a stack simplelock and must maintain sleep protocol correctness; owner tracking and `lockstatus` assertions can diverge from real lock state; modern and legacy paths differ significantly. Test signals are modern/legacy build coverage, lock debug builds, and wait/signal tests.
