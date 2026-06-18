# sources/distributed-fs/openafs/src/afs/IRIX/osi_sleep.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_sleep.c

Purpose: implements IRIX event-based sleep, timed sleep, wakeup, and wait-handle cancellation for OpenAFS.

Important APIs/types/functions: `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_getevent`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. It maintains `afs_evhasht` and `afs_evhashcnt` of `afs_event_t` entries.

Control flow: event addresses hash to condition-variable entries. Sleep records the current sequence and waits until wakeup increments it. Timed sleep computes a `timespec` and uses interruptible `sv_timedwait_sig` when requested, otherwise `cv_timedwait`. Wakeup gets the event, increments sequence, broadcasts if more than one reference exists, and releases it. Wait handles use static `waitV` for cancellation wakeups.

State/persistence: in-memory event table entries persist and are reused; refcounts manage active sleepers but entries are not freed. Wait handles store current thread pointer or zero when cancelled.

Dependencies/integration: depends on IRIX condition variables/state vectors and `afs_global_lock` from machdep macros.

Risks/test signals: risks include event table growth, missed wakeups if refcounts/sequence are wrong, interrupt handling, and global-lock reacquisition. Test timed waits, cancellation, multiple waiters on same event, signal-interruptible sleeps, and high churn event addresses.
