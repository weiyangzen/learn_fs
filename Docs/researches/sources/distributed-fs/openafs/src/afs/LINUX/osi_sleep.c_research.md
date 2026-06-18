# sources/distributed-fs/openafs/src/afs/LINUX/osi_sleep.c

## Purpose
This file implements OpenAFS sleep, timed sleep, wakeup, and wait-handle primitives on Linux using waitqueues and an event hash table keyed by event addresses.

## Important APIs, types, and functions
- `afs_osi_InitWaitHandle` initializes a wait handle.
- `afs_osi_CancelWait` cancels a wait by clearing its proc marker and waking the shared wait event.
- `afs_osi_Wait` waits for a timeout or cancellation using `afs_osi_TimedSleep`.
- `afs_evhasht` and `afs_evhashcnt` store event waitqueue records.
- `afs_getevent` and `afs_addevent` find or allocate event records.
- `afs_linux_sleep(event, killable)` implements interruptible or signal-masked sleeps.
- `afs_osi_SleepSig` and `afs_osi_Sleep` expose signal-aware and signal-blocking sleeps.
- `afs_osi_TimedSleep` sleeps with a millisecond timeout.
- `afs_osi_Wakeup` advances an event sequence and wakes waiters.

## Control flow and behavior
Events are looked up by hashing the event pointer. `afs_getevent` increments the refcount of a matching event or reuses a zero-refcount record in the bucket; `afs_addevent` allocates a new waitqueue record with a dummy event marker. Sleeping records the current event sequence, drops `AFS_GLOCK`, adjusts the current signal mask for killable or non-killable behavior, waits with freezer-aware waitqueue helpers until the sequence changes, restores the signal mask, reacquires `AFS_GLOCK`, normalizes `-ERESTARTSYS` to `EINTR`, and decrements the event refcount.

Timed sleep is similar but uses `wait_event_freezable_timeout` and does not adjust signal masks itself. Wakeup finds the event, increments its sequence only when more than one reference indicates sleepers are present, wakes the waitqueue, releases the lookup reference, and returns status codes indicating no sleepers, wake performed, or no wake.

## State and persistence
The event hash table and event records persist for module lifetime; event records are reused by setting `refcount` to zero but not freed in this file. Wait handles store a `proc` marker for cancellation. Signal masks are temporarily modified during sleeps.

## Dependencies and integration points
The code depends on Linux waitqueues, scheduler/freezer compatibility wrappers, signal locking macros from `osi_machdep.h`, OpenAFS global lock assertions, and AFS stats counters. It underlies broader cache manager waits, including dcache fetch waits and cancellation paths.

## Risks
Event records are never reclaimed here, so the table can grow with distinct event addresses until shutdown. `afs_getevent` returns NULL when no reusable record exists, forcing allocation, but allocation failure is not checked after `kzalloc` in `afs_addevent`. Wakeup requires `refcount > 1`; incorrect refcount handling can miss wakes. Signal mask manipulation must be exact or kernel threads may become unkillable/incorrectly interruptible. `afs_osi_Wait` computes end time in seconds from millisecond input, so subsecond precision is coarse.

## Test signals
Exercise sleep/wakeup with multiple waiters, timed sleep expiry, signal interruption through `SleepSig`, non-killable sleep signal masking, cancellation through wait handles, freezer behavior, many distinct event addresses, allocation failure injection, and shutdown leak checks.
