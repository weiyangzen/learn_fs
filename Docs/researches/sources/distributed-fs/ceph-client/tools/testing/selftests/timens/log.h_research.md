# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/log.h

## Purpose
Shared logging macros for time namespace selftests.

## Important APIs, Types, and Functions
Defines `pr_msg`, `pr_p`, `pr_err`, `pr_fail`, and `pr_perror`. The macros wrap kselftest output helpers and return `-1` for error/fail paths.

## Control Flow
No standalone execution. Test code calls these macros to print context-rich messages including file and line or errno-derived text.

## State and Persistence Behavior
No state is owned. Output is emitted through kselftest stdout/stderr conventions.

## Dependencies and Integration Points
Depends on `kselftest.h` functions such as `ksft_print_msg`, `ksft_test_result_error`, and `ksft_test_result_fail`. Included by timens C files.

## Risks and Edge Cases
Macros use GNU statement expressions, so they require a compatible compiler. `pr_p` relies on `%m` errno formatting.

## Test Signals
Signals are consistently formatted error and failure messages from time namespace tests.
