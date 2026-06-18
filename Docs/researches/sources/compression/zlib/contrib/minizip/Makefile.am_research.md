# sources/compression/zlib/contrib/minizip/Makefile.am

Purpose: defines the Automake/libtool build for minizip library, headers, pkg-config file, and optional demos.

Important APIs/types/functions: `lib_LTLIBRARIES = libminizip.la`, conditional `bin_PROGRAMS`, `libminizip_la_SOURCES`, `minizip_include_HEADERS`, `pkgconfig_DATA`, and demo program `LDADD` settings.

Control flow: Automake builds `libminizip.la` from core sources and optional `iowin32.c` on Windows. Headers install under `$(includedir)/minizip`. If demos are enabled, `miniunzip` and `minizip` are built and linked against the library and zlib.

State and persistence: produces libtool artifacts, optional binaries, installed headers, and `minizip.pc`.

Dependencies/integration: configured by `configure.ac` conditionals `COND_DEMOS` and `WIN32`, and uses zlib top source/build paths for include and library search.

Risks: links use `-lz` and build-tree `-L` assumptions rather than imported targets. Demo build is off unless configured. It does not encode all feature checks present in the newer CMake build.

Test signals: no explicit Automake test target in this file; successful build/install is the main signal.
