# sources/distributed-fs/lizardfs/tests/dispatcher/client/tests_list.py

## Purpose
`tests_list.py` extracts a filtered list of gtest test names for one LizardFS suite.

## Important APIs, Types, and Functions
`get_excluded_tests_two_types()` expands exclusions so both `Suite.test` and `test` forms are recognized. `get_gtest_testlist()` runs `lizardfs-tests --gtest_list_tests --gtest_filter=<suite>*`, skips the first two lines, and returns stripped test names not in the exclusion set.

## Control Flow
The dispatcher client calls `get_gtest_testlist()`, which shells out through `os.popen`, consumes gtest list output, and filters names.

## State and Persistence Behavior
No persistent state is written. The function depends entirely on the current executable output.

## Dependencies and Integration Points
It depends on Python standard `os` and generated gtest inventory from `lizardfs-tests`. It feeds `dispatcher_client.py`.

## Risks and Edge Cases
The command is assembled as a shell string, so paths or suite names with shell metacharacters are unsafe. Skipping exactly two lines assumes stable gtest output. Type hints expect `excluded_tests` as a list, while the CLI passes a string unless split elsewhere.

## Test Signals
Use fixture command output or monkeypatch `os.popen` to test exclusion expansion, suite filtering, empty output, and shell argument handling.
