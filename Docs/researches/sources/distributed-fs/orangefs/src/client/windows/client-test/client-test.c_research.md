# sources/distributed-fs/orangefs/src/client/windows/client-test/client-test.c

## Purpose
`client-test.c` is the command-line test runner for mounted OrangeFS client behavior. It validates a root directory, parses reporting and test-selection options, then runs registered filesystem operation tests.

## Important APIs, Types, And Functions
It defines an internal singly linked `list_node` for requested test names. Functions include `add_list_node`, `free_list`, `find_operation`, `setoption`, `init`, `run_tests`, `finalize`, and `main`. It consumes `global_options`, `test_operation`, and `op_table` from `test-support.h` and `test-list.h`.

## Control Flow
`main` requires a root directory, normalizes it with a trailing slash, allocates options and an empty test list, then calls `init`. `init` verifies the root is a directory and parses `-tabfile`, `-console`, `-file`, and explicit test names. `run_tests` runs all tests if the list is empty or resolves names through `find_operation` and runs them in requested order. Fatal test failures stop the run with `CODE_FATAL`; technical errors are reported with strerror.

## State And Persistence
State is in `global_options`, the transient test list, optional report file, and filesystem artifacts created by individual tests under `root_dir`.

## Dependencies And Integration Points
The runner uses Windows or POSIX stat APIs depending on platform and calls all test modules through `op_table`. Tests interact with OrangeFS only through the mounted path and C runtime filesystem calls.

## Risks And Test Signals
`free_list` frees the head node, so callers must not use it afterward. Some failure paths leak `options` or `test_list`. The runner stops at the first fatal/technical error, which is useful for smoke testing but can hide later failures. Its strongest signal is end-to-end compatibility of the mounted filesystem with ordinary CRT operations.
