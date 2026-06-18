## sources/distributed-fs/openafs/src/afs/NBSD/osi_sleep.c

Purpose: NetBSD sleep/wakeup/wait primitives for OpenAFS, with separate implementations for pre-NetBSD-5 `tsleep` and NetBSD-5+ condition-variable kernels.

Important APIs and state: defines `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, and `afs_osi_Wakeup`; NetBSD 5+ also defines `afs_osi_InitWaitHandle`, `afs_osi_TimedSleep`, event hash table `afs_evhasht`, and `afs_evhashcnt`. Static `waitV` is used for generic wait cancellation.

Control flow: older builds set a wait-handle proc, drop GLOCK, loop with `tsleep` until timeout, signal, or cancellation, then reacquire GLOCK. Sleep and wakeup map to `tsleep` and `wakeup`. NetBSD 5+ uses `afs_getevent` to map arbitrary event addresses to reusable `afs_event_t` entries containing a condition variable, sequence number, and refcount. Sleep waits while the sequence is unchanged; wakeup increments the sequence and broadcasts when there are waiters. Timed sleep uses `cv_timedwait` or `cv_timedwait_sig` with millisecond-to-tick conversion.

Dependencies and integration: depends on `afs_global_mtx` from `osi_machdep.h` for CV waits, OpenAFS GLOCK assertions, small-space allocation, stats counters, NetBSD time/tick APIs, and event structures from common AFS headers.

State and persistence: in-memory wait handles and event hash entries. Event structures are reused when refcount reaches zero but are not removed from the hash table in this file.

Risks: missed wakeups are prevented by sequence checks, but event reuse and refcount handling must stay under GLOCK. Older `tsleep` code drops GLOCK around blocking calls. `afs_osi_Wakeup` in the NetBSD 5+ path sets a local `ret` but returns 0 unconditionally, which may be intentional or a bug if callers rely on the return value.

Test signals: timed wait timeout vs signal, cancellation, multiple waiters on same event, repeated event reuse, interruptible sleep, wakeup return expectations, and lock-debug runs ensuring CV waits occur with `afs_global_mtx`.
