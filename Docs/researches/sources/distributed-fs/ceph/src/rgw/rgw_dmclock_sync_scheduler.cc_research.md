# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.cc

## Purpose
Implements the blocking/synchronous dmClock scheduler for RGW request paths that cannot use asynchronous completion directly.

## Important APIs, types, and functions
`SyncScheduler::add_request()` queues a stack-owned `SyncRequest`, updates counters, calls `request_completed()` to drive the dmClock push queue, and waits on a condition variable until ready or cancelled. `handle_request_cb()` marks a request ready, notifies the waiter, and updates latency/phase counters. `cancel(client)` and `cancel()` mark queued requests cancelled and notify waiters.

## Control flow
The caller blocks in `add_request()` until the dmClock callback fires. Cancellation removes matching queued requests, sets their state under their mutex, and wakes blocked callers.

## State and persistence
State is in-memory queue contents and per-request condition variables. No persistence occurs.

## Dependencies and integration points
Uses crimson dmClock push queue, scheduler context counters, Ceph perf counters, mutex/condition_variable, and the common scheduler interface.

## Risks and test signals
The queue stores references to synchronization objects whose lifetime is tied to the blocking stack frame, so callbacks must occur before `add_request()` returns. Tests should cover normal readiness, cancellation all/by client, limit rejection, counter decrements, spurious wakeups, and concurrent cancel while waiting.
