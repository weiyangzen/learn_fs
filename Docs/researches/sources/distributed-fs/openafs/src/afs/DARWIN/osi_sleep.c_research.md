# sources/distributed-fs/openafs/src/afs/DARWIN/osi_sleep.c

## Purpose
Implements Darwin sleep, timed sleep, wakeup, cancellation, and event-hash primitives used by OpenAFS while coordinating with the AFS global lock.

## Important APIs, Types, And Functions
Public routines include `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, `afs_osi_Wakeup`, `afs_osi_fullSigMask`, `afs_osi_fullSigRestore`, and `shutdown_osisleep`. `afs_getevent` maintains `afs_event_t` records in `afs_evhasht`.

## Control Flow
Wait handles store a process marker and use a shared `waitV` event. Event sleeps hash the event address, increment a refcount, snapshot a sequence number, drop the global lock while blocked on `msleep`, `sleep`, or `tsleep`, and resume when `afs_osi_Wakeup` increments the sequence. Timed sleep converts milliseconds to timespec or ticks and returns interrupt/timeout status. Shutdown walks event buckets and frees zero-refcount events.

## State And Persistence
Persistent state includes `afs_evhasht`, `afs_evhashcnt`, per-event sequence/refcount, and Darwin 8+ per-event mutex/owner fields. Wait handles persist a cancellation marker.

## Dependencies And Integration Points
Depends on Darwin sleep APIs, global lock macros, lock group `openafs_lck_grp`, OpenAFS allocation helpers, and all cache-manager code that waits for daemon, request, or vnode events.

## Risks
The event hash relies on pointer identity and sequence counters; missed wakeups can occur if refcounts or sequences are mishandled. Darwin 8+ event mutex owner assertions are strict. `afs_osi_TimedSleep` maps unchanged sequence to `EINTR`, which callers must interpret correctly. Shutdown can only free events with zero refcount.

## Test Signals
Exercise timed waits, cancelled waits, multi-waiter wakeups, interruptible sleeps, shutdown cleanup, and lock assertions under load. Repeated token, cache, and background daemon activity should not leak event records.
