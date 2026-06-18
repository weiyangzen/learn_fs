# sources/compression/zlib/contrib/puff/test/tester.cmake

Purpose: Minimal CMake runtime smoke test for the puff test executable.

Important APIs, types, and functions: Uses `execute_process` to run the executable path in `CMAKE_ARGV3` with `zeros.raw` from `CMAKE_ARGV4` as stdin, captures `RESULT_VARIABLE`, and emits `message(FATAL_ERROR)` on nonzero result.

Control flow: The script performs one command invocation and fails the CTest if the command exit code is nonzero.

State and persistence: No persistent state is written. It streams an input file into the test process.

Dependencies and integration points: Registered for shared and static puff test executables by `puff/test/CMakeLists.txt`.

Risks: It validates only one successful inflate path and does not inspect stdout/stderr. The fatal error text contains a typo, but behavior is unaffected.

Test signals: Confirms the built `pufftest` can successfully read and inflate the canonical `zeros.raw` input.
