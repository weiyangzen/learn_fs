# sources/distributed-fs/openafs/src/afs/HPUX/osi_sleep.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_sleep.c

Purpose: implements HP-UX sleep, timed wait, wakeup, and wait-handle cancellation abstractions for OpenAFS.

Important APIs/types/functions: `afs_osi_CallProc`, `afs_osi_CancelProc`, `AfsWaitHack`, `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, `afs_osi_Sleep`, and `afs_osi_Wakeup`. HP-UX 11 paths use `get_sleep_lock`; older paths use a static `waitV`.

Control flow: waits set a wait-handle process marker, schedule `AfsWaitHack` with `timeout`, sleep on either the handle/local event or `waitV`, cancel the timeout, and loop until timeout or cancellation. Cancellation clears the handle marker and wakes the event. HP-UX 11 functions explicitly drop/reacquire `AFS_GLOCK` around `sleep` because beta semaphores do not auto-release.

State/persistence: transient wait-handle state is stored in `achandle->proc`. No durable state. Timeout IDs are returned from HP-UX timeout APIs but not stored in the handle.

Dependencies/integration: depends on HP-UX `timeout`, `untimeout`, `sleep`, `wakeup`, sleep locks, and global lock semantics from `osi_machdep.h`.

Risks/test signals: risks include missed wakeups, cancellation races, timeout precision, and sleeping with incorrect global-lock state. Test timed sleeps, signal/cancel waits, wakeups before and during sleep, HP-UX 10 vs 11 builds, and shutdown paths.
