<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/common/CMakeLists.txt

## Purpose

This CMake file collects and builds the `mfscommon` shared library and its unit tests.

## Important APIs, Types, and Functions

Important build macros/functions are `include_directories`, `collect_sources(COMMON)`, `shared_add_library(mfscommon ...)`, `shared_target_link_libraries`, `create_unittest`, and `link_unittest`.

## Control Flow

CMake includes the common source directory, collects common sources, removes unsupported files on MinGW, removes alternative Galois-field implementations when ISA-L is available, builds `mfscommon`, conditionally links CRC, zlib, rt, allocator, socket, ISA-L, and Judy libraries, then builds the common unittest target with an extra master goal-config loader source.

## State and Persistence Behavior

It affects generated build-system state only. It does not create runtime persistence.

## Dependencies and Integration Points

This is the central build integration for all common files in this subset. It gates optional compression/checksum/allocator/socket/ISA-L support through CMake feature variables.

## Risks and Edge Cases

The `JEALLOC_LIBRARY` conditional links `${JEMALLOC_LIBRARY}`, suggesting a spelling mismatch that could skip or break jemalloc linkage depending on outer CMake variables. Removing Galois files under `ISAL_LIBRARY` assumes ISA-L replacements are complete.

## Test Signals

Signals are successful `mfscommon` builds on Linux and MinGW, optional-library matrix builds, and execution of `${COMMON_TESTS}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/CMakeLists.txt -->
