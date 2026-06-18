# sources/compression/zlib/contrib/blast/test/tester.cmake

Purpose: CMake script test runner for blast decompression fixtures.

Important inputs: `CMAKE_ARGV3` target executable, `CMAKE_ARGV4` source test directory, and `CMAKE_ARGV5` binary output directory.

Control flow: runs the executable with `test.pk` as input and writes `output.txt`, fails if the command returns nonzero, compares `output.txt` with `test.txt` using `cmake -E compare_files`, removes `output.txt`, and fails if files differ.

State and persistence: transiently writes and removes `output.txt` in the binary directory.

Dependencies and integration: invoked by CTest for shared and static blast test executables.

Risks: typo “exitited” in error message only affects diagnostics. If comparison fails, `output.txt` is still removed before the fatal error, which can make debugging harder.

Test signals: exact fixture comparison validates decompression output.
