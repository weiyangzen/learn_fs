# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.h

## Purpose
Declares the synchronous dmClock scheduler used for blocking RGW request scheduling.

## Important APIs, types, and functions
`SyncRequest` extends `Request` with references to a mutex, condition variable, mutable request state, and counters. `SyncScheduler` owns a dmClock `PushPriorityQueue`, exposes `add_request()`, cancellation APIs, and a static queue callback `handle_request_cb()`. Its scheduler implementation simply delegates `schedule_request_impl()` to `add_request()`.

## Control flow
Callers submit a request and block. The push queue invokes the static callback when dmClock chooses the request, which wakes the waiter.

## State and persistence
All state is transient queue state. Request synchronization members are non-owning references.

## Dependencies and integration points
Depends on common scheduler types, scheduler context counters, and crimson dmClock queue types.

## Risks and test signals
Because `SyncRequest` references stack locals, queue ownership/lifetime behavior is critical. Tests should validate no dangling callback after cancel/destruction, correct `ReqState` transitions, and callback cost/phase accounting.
