# sources/compression/zlib/contrib/puff/test/add_subdirectory_exclude_test.cmake.in

Purpose: Template for a consumer project that verifies puff can be embedded with `add_subdirectory(... EXCLUDE_FROM_ALL)`.

Important APIs, types, and functions: Declares project metadata, sets `ZLIB_PUFF_BUILD_TESTING` off, mirrors shared/static build options, calls `add_subdirectory`, builds `test_example` and/or `test_example_static`, and links `PUFF::PUFF` / `PUFF::PUFFSTATIC`.

Control flow: The generated project adds puff from the source tree while excluding puff's default targets from the all target. It then explicitly creates consumer executables only for enabled variants.

State and persistence: It only affects the generated test build directory and CMake target graph.

Dependencies and integration points: Depends on configured `@puff_SOURCE_DIR@`, `@puff_VERSION@`, and build-option substitutions from the parent test CMake.

Risks: The source list uses `pufftest.c`, which is a full CLI test driver, so target construction validates linking more than a library-like minimal API call. Behavior depends on the parent-provided shared/static option values.

Test signals: Parent CTest configures and builds this project to ensure exported alias targets are available even when puff is excluded from the default build.
