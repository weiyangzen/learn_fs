# sources/compression/zlib/contrib/minizip/test/add_subdirectory_test.cmake.in

## Purpose
This template validates consuming MiniZip as a normal CMake subdirectory.

## Important APIs, Types, and Functions
It sets MiniZip build options, calls `add_subdirectory(@minizip_SOURCE_DIR@ ...)`, defines sample executable sources, and links against `MINIZIP::minizip` and/or `MINIZIP::minizipstatic`.

## Control Flow
After configuration substitution, CTest configures this as a standalone project. It adds the MiniZip source tree, then conditionally defines one executable per enabled library variant.

## State and Persistence
Generated CMake files and build outputs live in the test work directory. No runtime persistence occurs unless the built sample executable is run elsewhere.

## Dependencies and Integration Points
Exercises MiniZip's subproject integration, alias targets, Windows IO source inclusion, and option propagation from the parent test.

## Risks and Edge Cases
As with the exclude variant, compiling `minizip.c` and `zip.c` directly into the test executable can hide missing transitive include or link details. The template does not run the executable; it only verifies configure/build.

## Test Signals
The parent `CMakeLists.txt` treats configure and build completion as the success criteria for subdirectory consumption.
