# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler.h

## Purpose
Defines the common RGW scheduler interface used by dmClock and simple throttling implementations.

## Important APIs, types, and functions
`Request` carries client id, start time, and cost. `ReqState` models blocking request state. `Completer<F>` is an RAII callback wrapper whose destructor calls its stored function. `Scheduler::schedule_request()` calls implementation-specific scheduling and returns both status and a `SchedulerCompleter` bound to `request_complete()`.

## Control flow
Callers schedule before processing a request. If accepted, holding the completer represents a granted unit; when the completer destructs, capacity is returned.

## State and persistence
The interface itself stores no state. Implementations maintain queue and throttle state.

## Dependencies and integration points
Depends on Ceph context/config/yield helpers and dmClock request parameter/time types. Used by sync, async, and simple throttler schedulers.

## Risks and test signals
The RAII completer is powerful but can call `request_complete()` even when scheduling failed unless callers handle the returned pair correctly. Tests should verify accepted and rejected request lifecycles, move-only completer behavior, and no double completion.
