# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_sleep.c

## Purpose
Solaris wait, sleep, timed sleep, signalable sleep, wakeup, and wait-handle primitives for OpenAFS.

## Important APIs, Types, and Functions
Defines `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. Maintains `afs_evhasht[AFS_EVHASHSIZE]`.

## Control Flow
Wait handles store `curthread`; cancellation clears the pointer and wakes a static wait variable. Event addresses are hashed to `afs_event_t` entries with condition variables and sequence counters. Sleeps wait on the event condvar while GLOCK is held by using `cv_wait`/`cv_wait_sig` on `afs_global_lock`. Timed sleep converts milliseconds to lbolt deadlines and uses timed condvar waits.

## State and Persistence
In-memory event table entries track event pointer, refcount, sequence, next pointer, and Solaris condition variable. No persistent state.

## Dependencies and Integration Points
Depends on Solaris condition variables, `afs_global_lock`, lbolt/DDI time APIs, and common AFS wait/event users.

## Risks
Event entries are reused but not freed. `afs_osi_Wakeup` calls `afs_getevent`, which creates an event entry even for wakeups with no sleepers. Return value currently always returns 0 despite tracking `ret`.

## Test Signals
Timed wait timeout and signal behavior, cancellation, wakeup broadcast to multiple sleepers, event reuse under churn, and lock assertions around condvar waits.
