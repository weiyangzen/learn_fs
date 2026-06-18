# sources/compression/zlib/contrib/minizip/test/find_package_no_components_test.cmake.in

## Purpose
This template validates `find_package(minizip CONFIG REQUIRED)` without explicit components.

## Important APIs, Types, and Functions
It calls `find_package(minizip ${minizip_VERSION} CONFIG REQUIRED)`, builds sample executables from MiniZip sources, and links to `MINIZIP::minizip` and `MINIZIP::minizipstatic` when corresponding options are enabled.

## Control Flow
The parent test configures this project after installing or preparing a package path. The project requests the package with no components, then conditionally links to shared and static targets based on substituted build options.

## State and Persistence
Only generated build-tree state is created. The test relies on the installed or build-tree CMake package config being available through the configured prefix or `ZLIB_DIR`.

## Dependencies and Integration Points
Exercises the no-component branch of `minizipConfig.cmake.in`, which expects both shared and static targets unless callers request a specific component.

## Risks and Edge Cases
The parent marks this configure test as `WILL_FAIL` when only one library variant was built. That means a failure is a success signal in one-variant builds and must be interpreted with build options.

## Test Signals
Success when both shared and static are present, expected configure failure otherwise. Link target availability is checked by generated executable targets.
