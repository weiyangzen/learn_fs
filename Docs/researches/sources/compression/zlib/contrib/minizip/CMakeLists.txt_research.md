# sources/compression/zlib/contrib/minizip/CMakeLists.txt

Purpose: builds, installs, packages, and optionally tests the minizip library and command-line tools.

Important APIs/types/functions: project `minizip`; options `MINIZIP_BUILD_SHARED`, `MINIZIP_BUILD_STATIC`, `MINIZIP_BUILD_TESTING`, `MINIZIP_ENABLE_BZIP2`, and `MINIZIP_INSTALL`; targets `libminizip`, `libminizipstatic`, `minizip`, `miniunzip`, and static tool variants; aliases `MINIZIP::minizip` and `MINIZIP::minizipstatic`.

Control flow: parent zlib options can seed minizip options. Standalone builds find required ZLIB components and optional BZip2. Configure checks detect `fopen64`, `fseeko`, `unistd.h`, `off64_t`, and hidden visibility. Shared/static libraries are built from `ioapi.c`, `mztools.c`, `unzip.c`, and `zip.c`; tools add `minizip.c` or `miniunz.c` plus platform I/O. Install rules export targets, generated config files, and headers.

State and persistence: affects CMake target graph, install tree, CPack metadata, and generated package config files.

Dependencies/integration: depends on zlib targets, optional BZip2, generated compile definitions for large file support and platform features, and a `test` subdirectory.

Risks: `MINIZIP_BUILD_TESTING` inherits `ZLIB_MINIZIP_INSTALL`, likely a copy-paste error. Static install has duplicate `COMPONENT` keywords. Shared version properties refer to `${zlib_VERSION_MAJOR}` and `${INSTALL_VERSION}`, which must be defined by the parent or may be empty.

Test signals: enables `add_subdirectory(test)` when testing is on; legacy Makefile also has a simple round-trip test.
