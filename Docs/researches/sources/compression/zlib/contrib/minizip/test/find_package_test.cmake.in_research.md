# sources/compression/zlib/contrib/minizip/test/find_package_test.cmake.in

## Purpose
This template validates explicit `find_package(minizip CONFIG COMPONENTS shared/static REQUIRED)` calls for downstream consumers.

## Important APIs, Types, and Functions
It conditionally calls `find_package(... COMPONENTS shared REQUIRED)` and/or `find_package(... COMPONENTS static REQUIRED)`, then links sample executables to `MINIZIP::minizip` or `MINIZIP::minizipstatic`.

## Control Flow
The generated project defines common sample sources first. If shared build support is enabled, it finds the shared component and creates `test_example`. If static support is enabled, it separately finds the static component and creates `test_example_static`.

## State and Persistence
State is limited to CMake configure variables, imported targets, and generated build artifacts.

## Dependencies and Integration Points
Directly exercises component-specific branches of the installed MiniZip package config and verifies that target files are included for requested components.

## Risks and Edge Cases
Running `find_package()` twice in one configure, once per component, depends on the config being idempotent with repeated calls. The sample executable includes MiniZip writer sources directly, so it is primarily a package-target availability check rather than a clean external API-only consumer.

## Test Signals
Configure and build success for each enabled component indicate that component-specific package discovery and imported targets work.
