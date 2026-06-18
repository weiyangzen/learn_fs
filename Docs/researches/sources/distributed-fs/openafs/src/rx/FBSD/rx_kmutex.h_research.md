# sources/distributed-fs/openafs/src/rx/FBSD/rx_kmutex.h

Purpose: maps Rx kernel locks/CVs to FreeBSD locking primitives.

Important APIs/types/functions: `afs_kmutex_t` as `struct sx` unless `NULL_LOCKS`, `afs_kcondvar_t` as `int`, `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `MUTEX_ASSERT`, and CV wake/sleep macros.

Control flow: normal builds use exclusive `sx` locks and `msleep` on CV addresses. `CV_WAIT` drops the AFS global lock if held, sleeps on the supplied lock, then restores the global lock. `NULL_LOCKS` only tracks `curproc` ownership for assertions.

State/persistence: `struct sx` lock state; optional owner pointer in null-lock builds.

Dependencies/integration: FreeBSD `sx` locks, `msleep`, `wakeup`, OpenAFS global lock, and optional WITNESS clearing.

Risks: `NULL_LOCKS` is not real synchronization; `msleep` lock semantics must match Rx expectations; WITNESS initialization changes are version-sensitive. Test signals are lock assertion failures, CV wakeups, and FreeBSD WITNESS builds.
