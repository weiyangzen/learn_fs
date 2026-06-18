# sources/distributed-fs/openafs/src/afs/AIX/osi_sleep.c

Purpose: AIX sleep, timed sleep, wait-handle, and wakeup implementation for OpenAFS kernel code.

Important APIs and functions: `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. `afs_getevent` maintains a hash table from event addresses to AIX event objects. `AfsWaitHack` clears timed waits from timer callbacks.

Control flow: waiters obtain an event record under `AFS_GLOCK`, assert wait on its condition, drop the global lock, block, then reacquire the lock. Timed sleeps allocate a `trb`, start it, block, stop/free it, and return `EINTR` only on interruption. Wakeup increments a sequence number and calls `e_wakeup` when waiters exist.

State and persistence: persistent in-kernel state is `afs_evhasht`, event refcounts, event sequence counters, and allocated pinned event records.

Dependencies and integration: uses AIX event and timer APIs, `pinned_heap`, global AFS lock assertions, and wait handles from common OpenAFS code.

Risks and test signals: `afs_getevent` reuses zero-refcount records but never frees them; timer allocation failure panics. Correct signals are absence of lost wakeups, expected timeout behavior, and no GLOCK misuse.
