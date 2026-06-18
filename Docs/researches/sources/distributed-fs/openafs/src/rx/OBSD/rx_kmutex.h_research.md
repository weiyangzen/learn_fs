# sources/distributed-fs/openafs/src/rx/OBSD/rx_kmutex.h

Purpose: OpenBSD Rx locking abstraction by ownership tracking and sleep/wakeup CVs.

Important APIs/types/functions: `afs_kmutex_t` with owner `struct proc *`, `afs_kcondvar_t` as `int`, macros `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `MUTEX_ASSERT`, `CV_WAIT`, `CV_SIGNAL`, and `CV_BROADCAST`.

Control flow: mutex enter/exit only asserts and records `curproc`; `CV_WAIT` drops the AFS global lock, exits the pseudo-mutex, sleeps with `tsleep`, then restores both.

State/persistence: owner pointer per pseudo-mutex; no real lock object.

Dependencies/integration: OpenBSD `tsleep`/`wakeup`, OpenAFS global lock, and current process.

Risks: header explicitly says it is incomplete and probably not suitable for `NCPUS > 1`; no real mutual exclusion exists. Test signals are limited to uniprocessor behavior, assertion checks, and careful SMP exclusion.
