# sources/distributed-fs/lizardfs/external/CMakeLists.txt

## Purpose
This CMake file builds the bundled crcutil library when a system crcutil is not found but CRC support is enabled.

## Important APIs, Types, and Functions
It checks `CRCUTIL_FOUND` and `HAVE_CRCUTIL`, includes `${CRCUTIL_INCLUDE_DIRS}`, appends crcutil-specific flags plus `-w` to suppress warnings, globs `${CRCUTIL_SOURCE_DIR}/*.cc`, and calls `shared_add_library(crcutil ...)`.

## Control Flow and State
The file does nothing when system crcutil is found or CRC support is disabled. Otherwise it builds a local `crcutil` target, possibly with a `_pic` variant when PIC targets are enabled.

## Dependencies and Integration Points
`Libraries.cmake` sets crcutil variables and top-level build adds `external` before source subdirectories. It depends on `SharedLibraries.cmake` helper functions already included.

## Risks and Edge Cases
It globally mutates `CMAKE_CXX_FLAGS` to add crcutil flags and disable warnings, which can leak to later targets. Globbing source files requires reconfiguration when bundled sources change.

## Test Signals
Build output should include the bundled `crcutil` target when system libcrcutil is absent on little-endian systems. CRC-enabled code link success validates it.
