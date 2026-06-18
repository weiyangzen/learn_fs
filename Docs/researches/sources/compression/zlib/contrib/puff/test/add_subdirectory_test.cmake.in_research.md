# sources/compression/zlib/contrib/puff/test/add_subdirectory_test.cmake.in

Purpose: Template for a consumer project that verifies normal source-tree embedding of puff with `add_subdirectory`.

Important APIs, types, and functions: Sets the generated project, disables puff's own tests, mirrors `ZLIB_PUFF_BUILD_SHARED` and `ZLIB_PUFF_BUILD_STATIC`, calls `add_subdirectory(@puff_SOURCE_DIR@ ...)`, and links generated test executables to `PUFF::PUFF` and `PUFF::PUFFSTATIC`.

Control flow: Configure-time options determine which executable targets are created. CMake then builds the consumer executables against the in-tree puff targets.

State and persistence: No persistent state beyond the generated build tree and target definitions.

Dependencies and integration points: Validates that puff's CMakeLists exports usable alias targets for in-tree consumers.

Risks: Because tests are disabled, this checks build/link integration but not runtime behavior. The consumer compiles `pufftest.c`, so any future dependency changes in that test driver can affect this integration test.

Test signals: Registered by the parent test suite as configure and build CTest entries with fixture ordering.
