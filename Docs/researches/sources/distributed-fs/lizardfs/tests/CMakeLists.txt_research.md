# sources/distributed-fs/lizardfs/tests/CMakeLists.txt

## Purpose
This CMake file wires the bash-based LizardFS test suite into a GoogleTest executable. It generates suite and case headers from `test_suites/`, configures runtime constants, and installs the `lizardfs-tests` runner.

## Important APIs, Types, and Functions
The `list_of_test_cases` custom target builds `test_suites.h` from suite directory names, runs `tools/generate_tests_from_templates.sh`, discovers `test_*.sh` files, optionally filters out polonaise tests, and emits `test_cases.h` entries using `add_test_case(suite,test)`. It configures `set_lizardfs_constants.sh` from the `.in` template and builds `lizardfs-tests` from `lizardfs-tests.cc`.

## Control Flow
At build time, generated headers are refreshed via `copy_if_different`; `lizardfs-tests.cc` has object dependencies on those headers and depends on `list_of_test_cases`. At runtime, each generated gtest case delegates to `run-test.sh`.

## State and Persistence Behavior
Generated state lives in the CMake binary directory: `test_suites.h`, `test_cases.h`, and `set_lizardfs_constants.sh`. Installed state includes the executable and constants script.

## Dependencies and Integration Points
It depends on GTest, Boost.System, Boost.Filesystem, shell utilities (`ls`, `find`, `sed`, `awk`, `xargs`), and the test template generator. It integrates the bash suite with CTest/GTest and packaging install paths.

## Risks and Edge Cases
The generated source property is assigned twice with `OBJECT_DEPENDS`; depending on CMake behavior, the second assignment may override the first. Shell discovery order and optional polonaise filtering can affect test inventory. Template generation must run before `find` output is consumed.

## Test Signals
Build validation should inspect generated headers, `--gtest_list_tests`, and polonaise-enabled/disabled configurations. A clean build should regenerate headers without causing needless rebuilds.
