# sources/distributed-fs/openafs/src/rx/SOLARIS/rx_kmutex.h

Purpose: Solaris kernel Rx mutex/CV macro mapping.

Important APIs/types/functions: `afs_kmutex_t` as `kmutex_t`, `afs_kcondvar_t` as `kcondvar_t`, macros `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `MUTEX_ASSERT`, `CV_INIT`, `CV_WAIT`, `CV_WAIT_SIG`, `CV_SIGNAL`, and `CV_BROADCAST`.

Control flow: regular paths delegate to Solaris `mutex_*` and `cv_*` primitives; `RX_LOCKS_DB` wraps lock enter/exit and CV waits with Rx lock-debug bookkeeping.

State/persistence: per-call-site kernel mutex/CV objects.

Dependencies/integration: Solaris `<sys/mutex.h>`, `<sys/t_lock.h>`, Rx lock debugging, and `afs_cv_wait` in the companion source.

Risks: only active for `AFS_SUN5_ENV && KERNEL`; debug wrappers must not alter lock ordering; `mutex_owned` assertion depends on Solaris ownership tracking. Test signals are Solaris kernel build, RX_LOCKS_DB build, and wait/signal lock-order tests.
