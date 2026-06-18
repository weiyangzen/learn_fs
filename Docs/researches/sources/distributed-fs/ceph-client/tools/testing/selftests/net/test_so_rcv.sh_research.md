# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_so_rcv.sh

## Purpose
`test_so_rcv.sh` is a shell harness for receive-side socket control-message tests. It validates `SO_RCVPRIORITY` and `SO_RCVMARK` delivery for IPv4 and IPv6 using companion listener and sender binaries.

## Important APIs, Types, And Functions
The script defines `check_result()` and `cleanup()`. It uses `setup_ns` and `cleanup_ns` from `lib.sh`, arrays for hosts and test argument mappings, and executes `./so_rcv_listener` and `./cmsg_sender`.

## Control Flow
The script creates one temporary namespace, then loops over `127.0.0.1` and `::1` and over two tests: `SO_RCVPRIORITY` with `-P 2` and `SO_RCVMARK` with `-M 3`. For each case it starts the listener in the namespace, waits briefly, runs the sender with matching arguments, waits for the listener, records success or failure, and prints per-case status. At the end it exits kselftest fail if any case failed, otherwise pass.

## State, Persistence, And Dependencies
State is the temporary namespace, the background listener PID, and counters `TOTAL_TESTS`/`FAILED_TESTS`. It depends on root namespace operations through `lib.sh`, the two compiled helper binaries, and support for the receive socket options under test.

## Integration Points
This harness pairs sender-generated control metadata with listener-side cmsg validation. It runs both address families in the same isolated namespace to avoid host socket state.

## Risks
The fixed `sleep 0.5` for listener readiness can be flaky on overloaded systems. Associative array iteration order is unspecified, though tests are independent. If the sender fails, the script kills and waits for the listener before continuing.

## Test Signals
Passing signal is `OK - All 4 tests passed` and `KSFT_PASS`. Failure signal is any sender failure or nonzero listener exit, reported as `FAIL - N/4 tests failed`.
