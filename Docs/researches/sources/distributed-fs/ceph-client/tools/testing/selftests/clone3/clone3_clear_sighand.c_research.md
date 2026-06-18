# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_clear_sighand.c

## Purpose

`clone3_clear_sighand.c` tests `CLONE_CLEAR_SIGHAND` semantics. It verifies mutual exclusion with `CLONE_SIGHAND` and that custom signal handlers are reset to defaults in the child. The complete 124-line file was read.

## Important APIs, Types, and Functions

Helpers include `nop_handler()`, local `wait_for_pid()`, and `test_clone3_clear_sighand()`.

## Control Flow

`main()` sets one planned test, verifies clone3 support, and calls the test. The test first expects `clone3(CLONE_CLEAR_SIGHAND | CLONE_SIGHAND)` not to succeed. It then installs no-op handlers for `SIGUSR1` and `SIGUSR2`, clones with `CLONE_CLEAR_SIGHAND`, and the child verifies both handlers are `SIG_DFL` before exiting successfully.

## State and Persistence Behavior

It modifies the current process signal dispositions for `SIGUSR1` and `SIGUSR2` and creates one short-lived child. It does not restore handlers before exit because it is a standalone test program.

## Dependencies and Integration Points

It depends on clone3 support, signal APIs, `CLONE_CLEAR_SIGHAND`, kselftest, and `clone3_selftests.h`.

## Risks and Edge Cases

The initial invalid clone check only fails if `pid > 0`; a zero child would be unexpected but not separately handled. Signal handler modifications are process-global but isolated to the test binary.

## Test Signals

Pass is reported when the child sees default handlers for both signals after `CLONE_CLEAR_SIGHAND`.
