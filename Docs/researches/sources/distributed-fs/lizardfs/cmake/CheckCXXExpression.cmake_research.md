# sources/distributed-fs/lizardfs/cmake/CheckCXXExpression.cmake

## Purpose
This helper defines `check_cxx_expression`, a CMake function for compile-time validation of a C++ boolean expression after including one or more headers.

## Important APIs, Types, and Functions
`check_cxx_expression(_EXPR _HEADER _RESULT)` builds source text containing `#include` lines for each header, a template that only defines `value_type` for `true`, and a `main` that instantiates the expression as a boolean. It calls `CHECK_CXX_SOURCE_COMPILES` with the generated source and stores the result in `_RESULT`.

## Control Flow and State
The function accumulates include directives, creates a single source string, and lets CMake's compiler-check machinery cache the result. There is no persistent runtime state; outputs are CMake cache/config variables consumed by `EnvTests.cmake` and ultimately `config.h.in`.

## Dependencies and Integration Points
It includes `CheckCXXSourceRuns`, though the implementation uses `CHECK_CXX_SOURCE_COMPILES`. It is used by `EnvTests.cmake` to check standard-library expressions such as steady-clock and allocator-traits support.

## Risks and Edge Cases
Header names are interpolated directly into angle-bracket includes. The check verifies compilation, not runtime behavior. The included module name is broader than necessary but harmless if CMake provides the compile macro elsewhere.

## Test Signals
Failures appear as false CMake variables such as `LIZARDFS_HAVE_STD_CHRONO_STEADY_CLOCK` or `LIZARDFS_HAVE_STD_ALLOCATOR_TRAITS`, influencing generated feature macros.
