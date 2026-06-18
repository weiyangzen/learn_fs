# sources/compression/zlib/test/find_package_no_components_test.cmake.in

This CMake template verifies `find_package(ZLIB @zlib_VERSION@ CONFIG REQUIRED)` without components. It checks that default config-mode package discovery exposes imported targets for the built zlib variants and can compile the `test/example.c` smoke program.

The script declares a C project, substitutes `ZLIB_BUILD_SHARED` and `ZLIB_BUILD_STATIC`, calls `find_package()`, then conditionally creates `test_example` linked to `ZLIB::ZLIB` and `test_example_static` linked to `ZLIB::ZLIBSTATIC`. Shared runtime execution is skipped for `.dll` suffixes; static execution is always registered when static is enabled.

State is limited to generated build targets and CTest metadata. Integration points are `zlibConfig.cmake.in`, exported component files, imported CMake targets, and `example.c`. A key risk is that no-component mode requires default targets to exist, which can fail single-variant builds unless users request a specific component. Test signals are configure/link success and CTest execution of the example binary.
