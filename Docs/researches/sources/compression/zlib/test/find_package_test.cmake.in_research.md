# sources/compression/zlib/test/find_package_test.cmake.in

This template validates explicit component lookup for zlib package config files. The shared branch requests `COMPONENTS shared` and links `ZLIB::ZLIB`; the static branch requests `COMPONENTS static` and links `ZLIB::ZLIBSTATIC`.

Control flow is split by substituted `ZLIB_BUILD_SHARED` and `ZLIB_BUILD_STATIC` options. Each enabled branch calls `find_package(ZLIB ... CONFIG COMPONENTS ... REQUIRED)`, builds `test/example.c`, links the component target, and registers a CTest test. Shared runtime tests are skipped on `.dll` platforms.

It persists only build-tree targets and test registrations. Integration is with `zlibConfig.cmake.in`, exported `ZLIB-shared.cmake`/`ZLIB-static.cmake`, and the public headers/libraries consumed by `example.c`. Risks are that disabled-component failure behavior is not tested here and DLL deployment is not runtime-validated. Passing configure/build/run confirms component metadata, imported-target properties, and basic zlib runtime behavior.
