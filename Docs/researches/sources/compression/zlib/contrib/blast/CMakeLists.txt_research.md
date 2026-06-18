# sources/compression/zlib/contrib/blast/CMakeLists.txt

Purpose: CMake build/install/package entry for the `blast` PKWare DCL decompression library.

Important APIs/options: project `blast` version `1.3.0`; options `ZLIB_BLAST_BUILD_SHARED`, `ZLIB_BLAST_BUILD_STATIC`, `ZLIB_BLAST_BUILD_TESTING`, and `ZLIB_BLAST_INSTALL`. Exports aliases `BLAST::BLAST` and `BLAST::BLASTSTATIC`.

Control flow: inherits root zlib contrib defaults when built from root, sets Windows static suffix and export-all behavior, builds shared and/or static libraries from `blast.c`/`blast.h`, adds tests when enabled, and installs targets, CMake package files, version files, and `blast.h`.

State and persistence: creates library artifacts, CMake export files, install tree entries, and configured package config files.

Dependencies and integration: uses GNUInstallDirs and CMakePackageConfigHelpers. The test subdirectory validates package consumption through `find_package` and `add_subdirectory`.

Risks: project description says “creating zipfiles based in zlib,” which does not match blast's decompression role. Shared install rules omit an explicit `LIBRARY DESTINATION`, relying on platform behavior.

Test signals: `contrib/blast/test/CMakeLists.txt` builds shared/static test executables and package-consumer fixtures.
