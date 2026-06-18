# sources/distributed-fs/openafs/src/rx/HPUX/rx_kmutex.h

Purpose: HP-UX Rx lock and condition variable abstraction, primarily for HP-UX 11 kernel builds.

Important APIs/types/functions: `afs_kmutex_t` as `b_sema_t`, `afs_kcondvar_t` as `caddr_t`, external `rx_sleepLock`, macros using `b_initsema`, `b_psema`, `b_vsema`, `b_cpsema`, `b_owns_sema`, `sleep`, `wakeup`, and `get_sleep_lock`.

Control flow: `CV_WAIT` obtains the sleep lock for the CV address, verifies the beta semaphore is held, releases it, sleeps, and reacquires it. Signal and broadcast both wake all sleepers via `wakeup`.

State/persistence: beta semaphore state per mutex; CV state is represented by wait-channel addresses rather than objects.

Dependencies/integration: HP-UX kernel sleep/spinlock/semaphore headers, network MP headers, and `osi_Panic`.

Risks: comments note missing/changed HP-UX APIs across 11.x releases; CV signal and broadcast are equivalent; non-11.0 paths can compile to no-op locks; ownership checks panic on misuse. Test signals are HP-UX version matrix builds, wait/signal behavior, and panic-free Rx lock use.
