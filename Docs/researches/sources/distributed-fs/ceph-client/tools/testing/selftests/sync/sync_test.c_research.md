# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_test.c

## Purpose
Provides the kselftest runner for the sync test suite. It checks environment support, runs each test function in an isolated child process, reports TAP-style kselftest results, and exits pass/fail/skip.

## Important APIs, Types, And Functions
Important functions are `run_test()`, `sync_api_supported()`, and `main()`. It uses `RUN_TEST()` from `synctest.h`, kselftest APIs such as `ksft_print_header()`, `ksft_set_plan()`, `ksft_test_result_pass()`, `ksft_test_result_fail()`, `ksft_get_fail_cnt()`, `ksft_exit_skip()`, `ksft_exit_fail_msg()`, and `ksft_exit_pass()`.

## Control Flow
`main()` prints the header, checks that `/sys/kernel/debug/sync/sw_sync` is present and accessible, sets a plan for ten tests, and invokes allocation, fence, wait, and stress tests. `run_test()` forks before executing each test; the parent waits and converts an exit status of zero into pass and nonzero or abnormal exit into failure. At the end it fails if any child test failed, otherwise exits pass.

## State And Persistence
The runner holds only process-local result state through kselftest counters. Forking isolates leaked fds, crashed tests, and mutated globals in each child.

## Dependencies And Integration Points
Depends on debugfs sw_sync, root or sufficient debugfs permissions, `../kselftest.h`, and all test prototypes from `synctest.h`. It is the executable listed by the sync selftest Makefile outside this assigned set.

## Risks
The plan is hard-coded as `3 + 7`; adding or removing tests requires updating it. A test terminated by signal is reported only as generic failure. `sync_api_supported()` skips on missing node or EACCES but fails other `stat()` errors.

## Test Signals
Useful signals are kselftest plan count matching executed tests, per-test pass/fail lines, skip when the sync framework is absent or inaccessible, and final aggregate pass only when no child test reports failure.
