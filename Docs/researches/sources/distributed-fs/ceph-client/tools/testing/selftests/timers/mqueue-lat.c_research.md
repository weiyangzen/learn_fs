# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/mqueue-lat.c

## Purpose
Measures POSIX message queue timed-receive timeout latency.

## Important APIs, Types, and Functions
Defines `TARGET_TIMEOUT` as 100 ms and `UNRESONABLE_LATENCY` as 40 ms. Functions are `timespec_sub`, `timespec_add`, `mqueue_lat_test`, and `main`.

## Control Flow
`mqueue_lat_test()` opens `/foo` as a read-only POSIX message queue, obtains message size, then performs 100 `mq_timedreceive()` calls on an empty queue with absolute realtime deadlines 100 ms in the future. It measures elapsed monotonic time and fails if average timeout exceeds target plus latency threshold. `main()` prints a status line and exits pass/fail.

## State and Persistence Behavior
Creates a POSIX message queue named `/foo` and closes it, but the source does not call `mq_unlink`, so the queue name may persist depending on system behavior and prior state.

## Dependencies and Integration Points
Depends on POSIX mqueue support, realtime library, `/dev/mqueue` availability/configuration, and kselftest. Integrates with `mq_timedreceive` timeout handling.

## Risks and Edge Cases
Lack of `mq_unlink` can leave stale `/foo`. Existing queue attributes may influence `mq_msgsize` if `/foo` already exists. Scheduler load can cause latency failures.

## Test Signals
Signals are `[OK]` when average timeout latency is within 40 ms of 100 ms, or failure on mqueue API errors/unreasonable latency.
