# sources/distributed-fs/openafs/src/rx/IRIX/rx_kmutex.h

Purpose: maps Rx locks/CVs to IRIX MP kernel synchronization primitives, with no-op fallbacks for non-MP builds.

Important APIs/types/functions: MP `afs_kmutex_t` as `kmutex_t`, `afs_kcondvar_t` as `kcondvar_t`, `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `CV_INIT`, `CV_WAIT`, `CV_SIGNAL`, and optional `RX_LOCKS_DB` wrappers.

Control flow: MP builds use `mutex_init`, `AFS_MUTEX_ENTER`, `mutex_tryenter`, `mutex_exit`, `sv_wait`, and `cv_*` primitives. `CV_WAIT` drops the AFS global lock while sleeping, then restores lock order. Non-MP builds make locks and CVs no-ops.

State/persistence: kernel mutex/CV objects in MP; none in non-MP.

Dependencies/integration: IRIX semaphore/CV APIs, current thread priority, Rx lock debug tracking, and OpenAFS global lock.

Risks: non-MP no-op locks are unsafe if compiled into a concurrent environment; `CV_WAIT` macro redefines `cv_wait`; debug and non-debug paths must stay behaviorally aligned. Test signals are MP lock-debug tests and CV wakeup tests.
