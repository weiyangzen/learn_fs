# sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_test.cmake.in

Purpose: Consumer-project template verifying ordinary `add_subdirectory` use of the zlib1-dll project.

Important APIs, types, and functions: Adds `@zlib1-dll_SOURCE_DIR@`, declares minizip example source files, creates two executables, and links against `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: The generated project configures zlib1-dll in a sub-build directory and then builds consumers against both DLL variants.

State and persistence: Only generated build-tree targets and CMake cache entries are produced.

Dependencies and integration points: Exercises in-tree aliases and include/link propagation from zlib1-dll to minizip consumers.

Risks: Since zlib1-dll hard-fails off Windows, this template is only meaningful in a Windows test environment. It does not execute the produced binaries.

Test signals: Parent configure/build CTest entries validate that both normal aliases link successfully.
