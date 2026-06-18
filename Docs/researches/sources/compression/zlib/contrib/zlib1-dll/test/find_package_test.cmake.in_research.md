# sources/compression/zlib/contrib/zlib1-dll/test/find_package_test.cmake.in

Purpose: Consumer-project template for installed `find_package(ZLIB1DLL)` behavior.

Important APIs, types, and functions: Defines a minizip source list, calls `find_package(ZLIB1DLL @zlib1-dll_VERSION@ CONFIG REQUIRED)`, creates `test_example` and `test_example_wapi`, and links imported `ZLIB1DLL::ZLIB1DLL` / `ZLIB1DLL::ZLIBWAPI`.

Control flow: Package discovery must succeed before consumer targets are created. The build then validates imported include paths and link libraries for both DLL variants.

State and persistence: Uses CMake cache state and installed package files from the private test prefix.

Dependencies and integration points: Exercises `zlib1dllConfig.cmake.in`, version files, installed exported targets, and minizip headers/sources.

Risks: Only validates configure/link, not runtime DLL loading. Version compatibility is `AnyNewerVersion` from the producer, so this test should accept newer patch-level configs but is pinned to the configured project version.

Test signals: Parent CTest runs configure and build after the install fixture.
