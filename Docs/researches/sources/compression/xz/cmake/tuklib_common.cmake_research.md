# sources/compression/xz/cmake/tuklib_common.cmake

## Purpose
This module provides shared helpers for the CMake versions of tuklib feature detection modules.

## Important APIs and Control Flow
`tuklib_add_definitions(TARGET_OR_ALL DEFINITIONS)` adds compile definitions either globally via `add_compile_definitions()` when passed `ALL`, or privately to a named target. `tuklib_add_definition_if(TARGET_OR_ALL VAR)` adds a definition only when the CMake variable evaluates true. `tuklib_use_system_extensions()` is a macro that adds common feature-test macros such as `_GNU_SOURCE`, `_DARWIN_C_SOURCE`, `_ALL_SOURCE`, and Solaris/NetBSD/OpenBSD variants, and appends matching `-D` entries to `CMAKE_REQUIRED_DEFINITIONS`.

## State, Dependencies, and Integration
It mutates global compile definitions and CMake check state. It is included by other `tuklib_*.cmake` modules and top-level `CMakeLists.txt`.

## Risks and Test Signals
Because system-extension macros affect feature checks and target compilation, ordering matters. The macro intentionally avoids MSVC. Cross-platform CI provides signal that these definitions expose needed APIs without breaking system headers.
