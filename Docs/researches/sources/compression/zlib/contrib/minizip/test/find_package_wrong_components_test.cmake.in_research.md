# sources/compression/zlib/contrib/minizip/test/find_package_wrong_components_test.cmake.in

## Purpose
This template verifies that MiniZip's CMake package config rejects unsupported components.

## Important APIs, Types, and Functions
It calls `find_package(minizip ${minizip_VERSION} CONFIG COMPONENTS wrong REQUIRED)`, then defines the same sample executable targets as the positive package tests.

## Control Flow
The parent CTest marks configure as `WILL_FAIL`, so the intended flow stops at package discovery because `wrong` is not in `_MINIZIP_supported_components`.

## State and Persistence
Only CMake configure state is expected, and successful failure should leave no meaningful build artifacts.

## Dependencies and Integration Points
Exercises the unsupported-component branch of `minizipConfig.cmake.in`, including `minizip_FOUND False` and not-found messaging.

## Risks and Edge Cases
If CMake package logic fails to reject the component, the rest of the template may configure and build, turning this into a regression signal. The template still defines targets after the failing call, but those should be unreachable due to `REQUIRED`.

## Test Signals
The expected signal is configure failure. Unexpected configure success indicates broken component validation.
