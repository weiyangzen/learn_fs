# sources/distributed-fs/openafs/src/afs/OBSD/osi_sleep.c

## Purpose
OpenBSD wait, sleep, timed sleep, wakeup, and time primitives for common OpenAFS code.

## Important APIs, Types, and Functions
Defines `osi_Time`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_TimedSleep`, `afs_osi_Sleep`, `afs_osi_SleepSig`, and `afs_osi_Wakeup`. Maintains `afs_evhasht[AFS_EVHASHSIZE]` and `afs_evhashcnt`.

## Control Flow
`afs_osi_Wait` computes a deadline, records the current process in the optional wait handle, drops GLOCK, and uses `tsleep` on a static wait variable until timeout, signal, or cancellation. Event sleep maps arbitrary event addresses into `afs_event_t` entries with sequence counters. Timed sleep records the current sequence, sleeps with `tsleep`, and treats unchanged sequence as interruption/timeout handling.

## State and Persistence
In-memory event hash entries are allocated and reused; each tracks event pointer, refcount, next pointer, and sequence. Wait handles store the sleeping process pointer. No persistent storage.

## Dependencies and Integration Points
Depends on OpenBSD `tsleep`, `wakeup`, `getmicrotime`, timer macros, and OpenAFS global lock discipline. Common AFS code uses this for cache waits, daemon coordination, and cancellation.

## Risks
Event entries are never freed, only reused when refcount reaches zero. Race behavior depends on GLOCK protection around event refcounts. `afs_osi_SleepSig` ignores signals and returns 0.

## Test Signals
Test timeout, interruptible wait, cancellation, wakeup sequencing, repeated event reuse, and lock assertions that sleep paths drop/reacquire GLOCK correctly.
