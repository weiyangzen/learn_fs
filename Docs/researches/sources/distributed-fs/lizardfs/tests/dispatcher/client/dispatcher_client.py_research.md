# sources/distributed-fs/lizardfs/tests/dispatcher/client/dispatcher_client.py

## Purpose
`dispatcher_client.py` is the command-line client for the test dispatcher. It pushes a filtered gtest list for a build/suite and retrieves the next test to run.

## Important APIs, Types, and Functions
`TESTS_DISPATCHER_URL` comes from the environment. `slash_join()` normalizes URL segments. `_call()` wraps requests for GET/POST/PUT/DELETE and JSON decoding. `push_list()` builds a list via `get_gtest_testlist()` and posts it. `next_test()` queries the dispatcher and returns the `details` field. The CLI parser exposes `--action`, `--build_id`, `--lizardfs_tests_path`, `--test_suite`, and `--excluded_tests`.

## Control Flow
For `push_list`, the client shells out through `tests_list.py` to list tests, sends JSON to `/push_list`, and returns the decoded response. For `next_test`, it sends build/suite parameters to `/next_test` and prints the next test name.

## State and Persistence Behavior
The client keeps no local state. Dispatcher state is remote and in-memory.

## Dependencies and Integration Points
It depends on `requests`, the local `tests_list` module, and the `lizardfs-tests` binary. It integrates with CI agents that split a suite across workers.

## Risks and Edge Cases
HTTP errors are logged gently and can return an empty string object, but `next_test()` assumes a `details` key and can raise. `excluded_tests` is typed as a string by argparse although `tests_list` expects a list, so callers must be careful about how exclusions are supplied. Connection and timeout errors exit the process.

## Test Signals
Mocked request tests should cover URL joining, duplicate push HTTP errors, connection failures, malformed JSON, missing `details`, exclusion handling, and CLI argument validation.
