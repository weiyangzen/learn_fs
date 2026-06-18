# sources/compression/zlib/contrib/minizip/test/add_subdirectory_exclude_test.cmake.in

## Purpose
This template creates a downstream CMake project that consumes MiniZip via `add_subdirectory(... EXCLUDE_FROM_ALL)` and verifies exported alias targets remain usable.

## Important APIs, Types, and Functions
It declares MiniZip build options, calls `add_subdirectory(@minizip_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, defines `MINIZIP_SRCS` with `ioapi.c`, optional `iowin32.c`, `minizip.c`, and `zip.c`, and links test executables to `MINIZIP::minizip` or `MINIZIP::minizipstatic`.

## Control Flow
The configured project adds MiniZip as an excluded child directory, then conditionally builds shared and/or static sample executables based on configured options.

## State and Persistence
State is confined to the generated downstream build tree. No installed package state is required.

## Dependencies and Integration Points
Exercises in-tree target aliases created by MiniZip's own CMakeLists, including behavior when the subdirectory is excluded from the default build.

## Risks and Edge Cases
Using MiniZip sample sources directly in the consumer executable can blur whether the linked library or local source objects provide symbols. The project name matches the non-exclude template, so logs can be confusing.

## Test Signals
Configure and build success indicate that `EXCLUDE_FROM_ALL` still leaves requested MiniZip targets addressable by downstream targets.
