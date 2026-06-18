# sources/distributed-fs/lizardfs/tests/lizardfs-tests.cc

## Purpose
`lizardfs-tests.cc` is the C++ GoogleTest bridge for bash system tests. It creates one gtest case per generated shell test and reports shell failures as gtest failures with captured error text.

## Important APIs, Types, and Functions
`BashTestEnvironment` creates and removes `/tmp/Lizardfs_bashtests_global_env`. `BashTestingSuite::run_test_case()` constructs `ERROR_FILE`, `TEST_SUITE_NAME`, and `TEST_CASE_NAME`, runs `run-test.sh` with the suite script, and reads the shared error file on failure. The `add_test_case` macro expands generated test entries into `TEST_F` bodies.

## Control Flow
The global environment prepares a world-writable temp directory. Each test creates an empty writable error file, calls the shell runner, and fails with either script crash text or the error file content. Generated `test_suites.h` and `test_cases.h` supply test classes and cases.

## State and Persistence Behavior
State is transient under `/tmp/Lizardfs_bashtests_global_env` and whatever the shell runner creates. The shared error file is outside per-test `TEMP_DIR` so it survives shell cleanup long enough for gtest to read it.

## Dependencies and Integration Points
It depends on GTest, Boost.Filesystem, generated headers, and `TEST_DATA_PATH` from CMake. It integrates with `run-test.sh` and the shell harness in `tools/test_main.sh`.

## Risks and Edge Cases
The command is assembled as a shell string, so paths with shell metacharacters would be risky. `system()` status is only checked for nonzero, not decoded. The global temp path is fixed, so concurrent independent runners could interfere.

## Test Signals
Signals include `--gtest_list_tests`, a deliberately failing shell test producing readable output, and concurrent runner isolation checks.
