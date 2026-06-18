<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.h -->
# sources/distributed-fs/lizardfs/src/common/io_limiting.h

## Purpose
Declares the high-level I/O limiting abstraction used by mounts, masters, and tests to request bandwidth assignments by I/O group and to wait on local group queues. The source was read completely for this report.

## Important APIs, Types, And Functions
`ioLimiting::Limiter::request`, `registerReconfigure`, `Clock`, `RTClock`, `SharedState`, and `Group::wait/die` define the public limiting contract. `Group` tracks pending requests, past requests, reservations, throttling delta, and a death flag.

## Control Flow
Callers register a reconfiguration callback, build shared limiter state, and call `Group::wait` while holding an external mutex. The group queues requests, asks the limiter/master when needed, reserves granted bytes, sleeps through the injected clock, and notifies queued waiters.

## State And Persistence Behavior
No file persistence. Runtime state is in per-group lists, reservation counters, timestamps for request pacing/freshness, condition variables, and the referenced limiter.

## Dependencies And Integration Points
Depends on `io_limit_group.h`, `io_limits_database.h`, and `time_utils.h`; integrates with master-side limit databases and mount-side throttling code.

## Risks And Edge Cases
Concurrency correctness depends on callers holding the expected mutex and on condition-variable notification order. Stale reservation timestamps or too-small deltas can over-throttle or over-request from the master.

## Test Signals
Test through limiter mocks, fake clocks, wait/deadline behavior, queue fairness, group removal wakeups, and integration with the database/token-bucket implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limiting.h -->
