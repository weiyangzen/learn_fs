# sources/distributed-fs/openafs/src/rx/LINUX/rx_kmutex.c

Purpose: Linux Rx kernel mutex and condition variable implementation.

Important APIs/types/functions: `afs_mutex_init`, `afs_mutex_enter`, `afs_mutex_tryenter`, `afs_mutex_exit`, and `afs_cv_wait`.

Control flow: mutex functions wrap Linux `struct mutex` while tracking owning pid and panicking on recursive/mismatched use. `afs_cv_wait` records the CV sequence, adds a wait queue entry, optionally blocks all signals, drops the AFS global lock and Rx mutex, schedules until signaled by a sequence change, restores signal masks, then reacquires locks.

State/persistence: per-mutex owner pid, per-CV sequence number and wait queue, socket/listener signal state indirectly through waiters.

Dependencies/integration: Linux mutex/waitqueue/scheduler APIs, OpenAFS `osi_compat`, `afs_try_to_freeze`, global lock macros, and Rx kernel panic/assert helpers.

Risks: signal masking and freezer interaction are kernel-version-sensitive; `owner` uses pid rather than task pointer; lost wakeups are avoided by sequence numbers but require all signal/broadcast paths to increment. Test signals are CV wait with and without signals, freezer paths, recursive lock panic tests, and SMP contention.
