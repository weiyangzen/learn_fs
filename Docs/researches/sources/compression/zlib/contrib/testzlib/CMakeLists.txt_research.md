# sources/compression/zlib/contrib/testzlib/CMakeLists.txt

Purpose: CMake build definition for the Windows-oriented `testzlib` benchmark/test executable.

Important APIs, types, and functions: Defines project metadata, options `ZLIB_TESTZLIB_BUILD_SHARED`, `ZLIB_TESTZLIB_BUILD_STATIC`, and `ZLIB_TESTZLIB_INSTALL`, computes `REQUIRED_COMPONENTS`, optionally calls `find_package(ZLIB REQUIRED COMPONENTS ... CONFIG)`, and creates shared/static-linked executable targets.

Control flow: When built from the main zlib project, options mirror top-level zlib build flags. Outside zlib, it discovers installed ZLIB components. It conditionally adds `testzlib` linked to `ZLIB::ZLIB` and `testzlibStatic` linked to `ZLIB::ZLIBSTATIC`, then optionally installs runtime executables.

State and persistence: Mutates CMake cache options and install rules. No tests are registered here.

Dependencies and integration points: Integrates with zlib's CMake package targets and install directory variables. The source itself depends on Windows APIs, so successful compilation is platform-specific.

Risks: Shared/static requested components must match available package exports. The script defaults to building both variants, which can fail if only one installed component exists. It does not guard `testzlib.c`'s Windows-only headers.

Test signals: Build/link success is the primary signal. Runtime validation is manual through the produced executable.
