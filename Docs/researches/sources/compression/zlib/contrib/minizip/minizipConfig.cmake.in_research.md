# sources/compression/zlib/contrib/minizip/minizipConfig.cmake.in

## Purpose
This CMake package configuration template lets downstream projects call `find_package(minizip CONFIG ...)` and import shared and/or static MiniZip targets.

## Important APIs, Types, and Functions
- `_MINIZIP_supported_components` lists valid components: `shared` and `static`.
- `minizip_HAS_BZIP2` records whether the installed package was built with bzip2 support.
- Uses `find_dependency(ZLIB CONFIG ...)` and optionally `find_dependency(BZip2)`.
- Includes generated target files `minizip-shared.cmake` and `minizip-static.cmake`.
- Sets `minizip_<component>_FOUND`, `minizip_FOUND`, and `minizip_NOT_FOUND_MESSAGE` for component validation.

## Control Flow
After dependency setup, the file branches on `minizip_FIND_COMPONENTS`. With explicit components it validates each requested component, includes the matching target file, and marks that component found. Without components it loads both optional target files and expects both `MINIZIP::minizip` and `MINIZIP::minizipstatic` to exist; otherwise it marks the package not found with guidance to request a specific component.

## State and Persistence
The installed config persists build-time choices such as bzip2 enablement and installed target availability. During `find_package()` it mutates CMake cache/package variables only for the current configure run.

## Dependencies and Integration Points
Integrates with CMake package consumers, exported MiniZip target files, zlib's CMake package, and optionally BZip2. The test templates under `contrib/minizip/test` validate component and no-component behavior.

## Risks and Edge Cases
The no-component branch requires both shared and static targets, so installs with only one library type intentionally fail unless the caller requests `COMPONENTS shared` or `static`. Error messages mention `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC` in conditions that actually test MiniZip targets, which can confuse consumers. Component validation still calls `find_dependency(ZLIB CONFIG COMPONENTS ${minizip_FIND_COMPONENTS})`, assuming zlib component names align with MiniZip component names.

## Test Signals
`find_package_test.cmake.in`, `find_package_no_components_test.cmake.in`, and `find_package_wrong_components_test.cmake.in` cover explicit components, no components, and unsupported component failure.
