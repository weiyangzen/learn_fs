# sources/distributed-fs/lizardfs/cmake/SharedLibraries.cmake

## Purpose
This module provides helper functions to build paired static and position-independent libraries for components that may be linked into shared libraries.

## Important APIs, Types, and Functions
`shared_add_library(NAME ...)` creates a normal library and, when `ENABLE_PIC_TARGETS` is true, an additional `${NAME}_pic` library from the same sources with position-independent code. `shared_target_link_libraries(TARGET ...)` links the normal target and, when PIC targets are enabled, links the PIC target with PIC equivalents where available.

## Control Flow and State
`shared_target_link_libraries` parses mode tokens `STATIC`, `SHARED`, and `MIXED`. In mixed mode it links static targets against the original library and PIC targets against `${library}_pic` if that target exists. It mutates target link libraries for both target variants.

## Dependencies and Integration Points
Included by `EnvTests.cmake`, then used by external and source subdirectories. Top-level `CMakeLists.txt` sets `ENABLE_PIC_TARGETS` when `ENABLE_CLIENT_LIB` is enabled.

## Risks and Edge Cases
The function signature uses variadic syntax compatible with older CMake patterns. Target existence checks are simple and depend on consistent `_pic` naming. Incorrect scan-mode ordering can link dependencies to only one variant.

## Test Signals
Building with `ENABLE_CLIENT_LIB=ON` should produce `_pic` library variants and shared-client link success. Static-only builds should produce only normal targets.
