# sources/distributed-fs/lizardfs/src/chunkserver/CMakeLists.txt

## Purpose
This CMake file defines how the LizardFS chunkserver component is built, tested, linked, and installed.

## Important APIs, Types, And Functions
- `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` exposes chunkserver local headers to this target tree.
- `add_definitions` sets `LIZARDFS_MAX_FILES=10000`, `APPNAME=mfschunkserver`, and `APP_EXAMPLES_SUBDIR`.
- `collect_sources(CHUNKSERVER)` populates `${CHUNKSERVER_SOURCES}`, `${CHUNKSERVER_TESTS}`, and `${MAIN_SRC}` through repository-local CMake helpers.
- `add_library(chunkserver ...)` builds the reusable chunkserver library.
- `create_unittest` and `link_unittest` wire chunkserver tests against `chunkserver` and `mfscommon`.
- `add_executable(mfschunkserver ${MAIN_SRC})` produces the daemon binary.

## Control Flow
CMake first applies compile definitions, collects sources, creates the library, registers tests, then creates the executable. The executable links the chunkserver library and PAM libraries, and conditionally links systemd libraries when detected.

## State And Persistence
There is no runtime state here. Build state is represented in generated build-system files and install output. Installation places `mfschunkserver` into `${SBIN_SUBDIR}`.

## Dependencies And Integration Points
The chunkserver library links `lzfsprotocol`, `mfscommon`, and `${ADDITIONAL_LIBS}`. The executable links PAM and optionally systemd. The file depends on project-specific CMake functions/macros such as `collect_sources`, `create_unittest`, and `link_unittest`.

## Risks
Because `collect_sources` is opaque in this file, adding or renaming chunkserver source files depends on that helper discovering the files correctly. Global `add_definitions` applies to everything below this directory and can have wider compile effects than target-scoped definitions.

## Test Signals
The explicit `create_unittest` and `link_unittest` calls show the chunkserver target has an associated test suite compiled from `${CHUNKSERVER_TESTS}`.
