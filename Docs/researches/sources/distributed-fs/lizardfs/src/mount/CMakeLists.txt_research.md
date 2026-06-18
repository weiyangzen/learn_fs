# sources/distributed-fs/lizardfs/src/mount/CMakeLists.txt

## Purpose
This CMake file defines the core `mount` shared library build and its unit-test target, and conditionally enters the client library subdirectory.

## Important APIs, Types, And Functions
- `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` exposes mount headers to local targets.
- `collect_sources(MOUNT)` gathers source and test lists according to project macros.
- `shared_add_library(mount ${MOUNT_SOURCES})` builds the shared/static/PIC variants expected by the repository.
- `create_unittest(mount ${MOUNT_TESTS})` and `link_unittest(mount mount mfscommon)` wire mount tests.
- `if (ENABLE_CLIENT_LIB) add_subdirectory(client) endif()` controls client library builds.

## Control Flow
CMake first gathers all mount sources, builds the `mount` library linked against `mfscommon` and additional platform libraries, creates tests, then optionally builds C/C++ client wrappers.

## State And Persistence
This file contributes build graph state only. It does not create runtime state or installed artifacts directly except through targets.

## Dependencies And Integration Points
It relies on project-defined macros such as `collect_sources`, `shared_add_library`, `shared_target_link_libraries`, `create_unittest`, and `link_unittest`. The client subdirectory depends on `ENABLE_CLIENT_LIB`.

## Risks
- Broad `include_directories` affects all following targets in this directory scope.
- Source collection depends on project macros; missing or misclassified files in those macros can silently change library contents.

## Test Signals
Build configuration tests should cover `ENABLE_CLIENT_LIB` on/off and validate that mount unit tests link with `mount` and `mfscommon`.
