# sources/distributed-fs/openafs/src/afs/FBSD/osi_sleep.c

## Purpose
Implements FreeBSD wait-handle, event sleep, timed sleep, and wakeup primitives for OpenAFS.

## Important APIs, Types, And Functions
Exports `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. Static `afs_getevent` maintains event records in `afs_evhasht`.

## Control Flow
Wait handles use FreeBSD condition variables under `afs_global_mtx`; waits convert milliseconds to ticks and call `cv_timedwait` or `cv_timedwait_sig`. Address-based event sleeps hash the event pointer, snapshot a sequence, and sleep on the address with `msleep` until `afs_osi_Wakeup` increments the sequence and calls `wakeup`.

## State And Persistence
Persistent state includes per-wait-handle condition variables and initialization flags, global event hash `afs_evhasht`, per-event sequence/refcount, and `afs_evhashcnt`.

## Dependencies And Integration Points
Depends on FreeBSD `cv_*`, `msleep`, `wakeup`, `tvtohz`, `afs_global_mtx`, and generic OpenAFS daemon/request wait code.

## Risks
Wait handles are lazily initialized in some paths, noted as questionable by comments. Event records are allocated no-sleep and are not freed here. Return codes from `cv_timedwait`/`msleep` must be interpreted consistently by callers.

## Test Signals
Exercise timed waits, interruptible waits, cancel waits, event wakeups with multiple waiters, and long-running daemon workloads for event-hash growth or missed wakeups.
