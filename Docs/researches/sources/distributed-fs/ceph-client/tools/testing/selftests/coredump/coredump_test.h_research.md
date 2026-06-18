# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test.h

## Purpose

`coredump_test.h` is the shared declaration and fixture header for coredump selftests. It centralizes fixture state, helper prototypes, protocol helpers, and the server wait helper used by stackdump and socket tests.

## Important APIs, Types, and Functions

It defines `FIXTURE(coredump)` with `original_core_pattern`, `pid_coredump_server`, and `fd_tmpfs_detached`. It declares helpers for crashing child creation, detached tmpfs creation, socket listener setup, `core_pattern` writing, peer pidfd lookup, pidfd info reads, coredump request/ack protocol handling, temporary core-file opening, and epoll worker processing. `wait_and_check_coredump_server()` wraps `waitpid()` and harness assertions.

## Control Flow

There is no standalone test flow. Including tests instantiate setup/teardown functions and call helpers. The inline wait helper marks the server as gone by storing `-ESRCH`, then asserts normal exit status 0.

## State and Persistence Behavior

The fixture state is per-test and tracks persistent host modifications to `core_pattern`, coredump server lifetime, and a detached tmpfs fd that must be closed in teardown.

## Dependencies and Integration Points

It depends on `<linux/coredump.h>`, `kselftest_harness.h`, pidfd test helpers, and the implementation in `coredump_test_helpers.c`. It defines the contract that socket and stackdump tests rely on.

## Risks and Edge Cases

Fixture cleanup correctness is essential because a failed test can otherwise leave `core_pattern` changed or a server process alive. The helper assumes server success is represented by a normal exit code of 0.

## Test Signals

The header enables tests to report harness assertions consistently. `wait_and_check_coredump_server()` failure identifies coredump server-side protocol or copy failures.
