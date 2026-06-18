# sources/distributed-fs/openafs/src/rx/AIX/rx_kmutex.h

Purpose: maps Rx kernel locks and condition variables to AIX 4.1+ simple locks and event-list sleep/wakeup primitives.

Important APIs/types/functions: `afs_kmutex_t` as `simple_lock_data`, `afs_kcondvar_t` as `tid_t`, macros `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `MUTEX_DESTROY`, `MUTEX_ASSERT`, `CV_INIT`, `CV_WAIT`, `CV_SIGNAL`, and `CV_BROADCAST`.

Control flow: `CV_WAIT` releases the AFS global lock when held, sleeps through `e_sleep_thread`, then restores the global-lock/mutex ordering. Under `RX_LOCKS_DB`, enter/exit/wait paths also update Rx lock debugging.

State/persistence: lock allocation state is pinned via `lock_alloc`; condition variables are event identifiers initialized to `EVENT_NULL`.

Dependencies/integration: depends on AIX lock, sleep, thread, and OpenAFS global-lock primitives. Used by Rx kernel shared code via `rx_kcommon.h`.

Risks: AIX event-list semantics can lose signals issued before waiters sleep; global-lock reacquisition ordering is delicate; debug and non-debug macros must remain equivalent. Test signals are lock-debug builds, wait/signal wakeups, and Rx shutdown without deadlock.
