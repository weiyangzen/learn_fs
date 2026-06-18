# sources/compression/zlib/CMakeLists.txt

Purpose: primary CMake build, install, package, and test entry point for zlib.

Important APIs/options: project `zlib` version `1.3.2.1`; options `ZLIB_BUILD_TESTING`, `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `ZLIB_INSTALL`, and `ZLIB_PREFIX`. Uses feature checks for `off64_t`, `fseeko`, `stdarg.h`, `unistd.h`, and hidden visibility. Exports targets `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`.

Control flow: sets a default Release build for single-config generators, generates a CMake-specific `zconf.h.cmakein` from `zconf.h`, runs platform feature checks, configures `zlib.pc` and `zconf.h`, declares source/header lists, builds shared and/or static libraries, sets platform-specific names/version scripts, installs exports/config files/headers/docs/pkg-config metadata, enables tests, and always enters `contrib`.

State and persistence: writes generated `zconf.h.cmakein`, `zconf.h`, `zlib.pc`, CMake package config files, build artifacts, install tree content, and CPack metadata.

Dependencies and integration: integrates with CMakePackageConfigHelpers, CPack, GNUInstallDirs, the `test` subdirectory, and all contrib option dispatch. Consumers use installed `ZLIBConfig.cmake` or pkg-config.

Risks: the `zconf.h` generation uses fixed read offsets from the source header, so upstream header layout changes can break generated content. Version-script linking excludes AIX and SunOS but may need maintenance for more Unix variants. Building contrib unconditionally delegates option checks to `contrib/CMakeLists.txt`.

Test signals: `ZLIB_BUILD_TESTING` enables the `test` subdirectory; CI workflows also validate packaging, install exports, shared/static variants, and minizip integration.
