# sources/compression/zlib/.github/workflows/cmake.yml

Purpose: primary CMake CI workflow for zlib shared/static/package variants on Linux, macOS, and Windows.

Important jobs/settings: `ci-cmake` matrix includes GCC, Clang, MSVC Win32/Win64/ARM64, Windows GCC/Ninja, and multiple macOS GCC versions. It toggles `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `ZLIB_BUILD_MINIZIP`, `MINIZIP_ENABLE_BZIP2`, and build type.

Control flow: installs platform packages (`nsis` on Windows, `libbz2-dev` on Linux), configures into `../build`, builds, runs CTest from that build directory, builds package targets, and uploads CMake logs on failure.

State and persistence: CI build outputs live outside the checkout in `../build`; failure artifacts retain CMake logs for seven days.

Dependencies and integration: uses `actions/checkout@v6`, CMake/CPack, NSIS, bzip2 development headers, compilers, and zlib install/package rules.

Risks: `ctest -C Release` is used even for the Debug matrix item, which can be harmless for single-config generators but is a mismatch risk. Package target names differ by generator/platform and are encoded in the matrix.

Test signals: validates CMake configure/build/test/package behavior for shared-only, static-only, optimized, debug, and minizip-enabled builds.
