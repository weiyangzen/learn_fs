# sources/compression/zlib/test/find_package_wrong_components_test.cmake.in

This template is the negative package-config test. It calls `find_package(ZLIB @zlib_VERSION@ CONFIG COMPONENTS wrong REQUIRED)` and expects configuration to fail because `wrong` is not a supported component.

The later shared/static `example.c` target creation mirrors the positive tests, but should be unreachable if component validation works. The relevant integration point is `_ZLIB_supported_components` in `zlibConfig.cmake.in`, which should set `ZLIB_FOUND` false and report `Unsupported component: wrong`.

No runtime state is persisted beyond CMake configure logs. The main risk is harness interpretation: configure failure is the expected success signal for this test. Unexpected configure success means invalid components are being accepted and the package contract is too permissive.
