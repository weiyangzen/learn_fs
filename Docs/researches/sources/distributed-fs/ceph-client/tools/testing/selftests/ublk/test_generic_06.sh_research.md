# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_06.sh

## Purpose
This fault-injection test checks that I/O fails quickly when the ublk server dies with I/O outstanding in the server.

## Important APIs, Types, and Functions
It creates a fault-inject device with `--delay_us 2000000`, starts a direct `dd` write from `/dev/urandom`, uses `__ublk_kill_daemon()` to force the daemon to `DEAD`, and measures shell `SECONDS`.

## Control Flow
The script starts one delayed direct write, kills the daemon, waits for `dd`, and fails if `dd` exits successfully or if elapsed time is at least 5 seconds. It expects fast failure rather than waiting for long block I/O timeout.

## State and Persistence
It creates a temporary fault-inject ublk device and background `dd` process, then cleans up.

## Dependencies and Integration Points
It depends on `fault_inject.c`, daemon death handling in the ublk driver, and common shell cleanup.

## Risks
Timing is scheduler-dependent, but the 5 second threshold allows some tolerance. If device cleanup hangs, the test runner may time out externally.

## Test Signals
Pass means outstanding I/O observes server death quickly and returns an error.
