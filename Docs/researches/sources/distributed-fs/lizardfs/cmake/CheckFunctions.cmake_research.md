# sources/distributed-fs/lizardfs/cmake/CheckFunctions.cmake

## Purpose
This module centralizes function-existence probes for C and C++ build configuration.

## Important APIs, Types, and Functions
`check_functions(FUNCTIONS REQUIRED)` loops over function names, creates uppercase `LIZARDFS_HAVE_<FUNC>` variables, calls `CHECK_FUNCTION_EXISTS`, and emits `SEND_ERROR` when required functions are missing. `check_template_function_exists(HEADER CALL OUTPUT_VARIABLE)` compiles a small C++ program including `HEADER` and executing `CALL`.

## Control Flow and State
The functions set CMake cache/config variables consumed later by `config.h.in`. Required failures do not immediately call `FATAL_ERROR`, but `SEND_ERROR` makes configuration fail at generation.

## Dependencies and Integration Points
`EnvTests.cmake` invokes these helpers for POSIX functions, optional functions, and standard-library template functions. The caller is responsible for including CMake's `CheckFunctionExists` and `CheckCXXSourceCompiles` modules.

## Risks and Edge Cases
The required check tests for empty string or non-`1` values and may be sensitive to CMake truthiness. The template helper only checks if the output variable is undefined, so stale cache values can mask compiler changes.

## Test Signals
Configuration output and generated `LIZARDFS_HAVE_*` macros are the main signals. Missing required functions produce CMake errors.
