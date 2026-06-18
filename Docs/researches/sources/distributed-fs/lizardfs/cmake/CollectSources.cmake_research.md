# sources/distributed-fs/lizardfs/cmake/CollectSources.cmake

## Purpose
This macro provides a conventional way for subdirectories to collect local sources, tests, and main files.

## Important APIs, Types, and Functions
`collect_sources(VAR_PREFIX)` populates `${VAR_PREFIX}_TESTS` with `*_unittest.cc`, `${VAR_PREFIX}_SOURCES` with local `.cc`, `.c`, and `.h`, and `${VAR_PREFIX}_MAIN` with `main.cc` or `main.c`. If main or test files exist, it removes them from the generic source list.

## Control Flow and State
The macro uses CMake `file(GLOB ...)` at configure time. It mutates variables named by prefix in the caller's scope.

## Dependencies and Integration Points
Included by top-level `CMakeLists.txt`, it is intended for source subdirectories that build libraries, binaries, and unit-test libraries from consistent naming conventions.

## Risks and Edge Cases
Globbing is configure-time only, so adding source files may require rerunning CMake. The `if(${VAR_PREFIX}_MAIN OR ${VAR_PREFIX}_TESTS)` expression can be brittle when variables expand to lists with special content. Only one directory level is scanned.

## Test Signals
Build target source lists are the practical signal. Missing files in targets after adding new sources suggests CMake was not rerun or naming conventions were not followed.
