# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/harness.c

## Purpose
Process-isolating test harness used by many PowerPC C selftests.

## Important APIs, Types, and Functions
Defines `KILL_TIMEOUT`, `run_test()`, `sig_handler()`, `test_harness_set_timeout()`, and `test_harness()`, and emits subunit results through `subunit.h` helpers.

## Control Flow
`test_harness()` installs timeout signal handling, forks the test function in a child, waits with timeout handling, kills hung children, and reports pass/fail/skip based on exit status and signals.

## State and Persistence
State includes global timeout configuration, child process state, signal alarms, and subunit output. No files are persisted.

## Dependencies and Integration Points
Depends on fork/wait/signal/alarm, `utils.h` result conventions, and `subunit.h` output formatting.

## Risks and Test Signals
Risks include masking child signal details or timeout races. Test signal is consistent subunit reporting and cleanup of hung tests.
