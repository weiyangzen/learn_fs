# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/taprio_wait_for_admin.sh

## Purpose
Polls a taprio qdisc until an admin schedule is visible, helping tests wait for asynchronous taprio state publication.

## Important APIs, Types, And Functions
Uses shell variables `TC`, `DEV`, `handle`, `query`, `taprio`, and `MAX_WAIT`. It runs `tc qdisc show dev "$DEV"` repeatedly and greps for the expected taprio handle plus `admin`.

## Control Flow
The script loops for up to 20 seconds. Each second it checks whether the qdisc output contains the requested handle with `taprio` and an admin schedule; if so it exits success. After the timeout it exits failure.

## State And Persistence
No persistent state. It observes qdisc state on the device provided by arguments.

## Dependencies And Integration Points
Depends on `tc`, a target interface, taprio qdisc support, and tests that pass the correct qdisc handle.

## Risks
String matching is simple and can break if `tc qdisc show` formatting changes. Polling at one-second granularity can add up to 20 seconds to failing tests.

## Test Signals
Exit status `0` when admin schedule appears; exit status `1` after timeout.
