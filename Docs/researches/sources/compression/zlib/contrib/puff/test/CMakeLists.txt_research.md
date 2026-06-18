# sources/compression/zlib/contrib/puff/test/CMakeLists.txt

Purpose: Defines CTest coverage for puff runtime behavior and CMake integration scenarios.

Important APIs, types, and functions: Uses `add_test`, `set_tests_properties`, fixtures, `configure_file`, generator/platform propagation, `add_executable`, `target_link_libraries`, and optional gcov coverage targets. Key variables include `ZLIB_PUFF_BUILD_SHARED`, `ZLIB_PUFF_BUILD_STATIC`, `ZLIB_BUILD_PUFF`, `WORK_DIR`, `inst_setup`, `ZLIB_ARG`, `GCOV_EXECUTABLE`, and `ZLIB_CONTRIB_PREFIX`.

Control flow: When puff is tested standalone, it first installs puff into a private prefix and uses a fixture. It builds shared/static `pufftest` executables on non-Windows, optionally with coverage instrumentation. It then configures template projects for `find_package`, `add_subdirectory`, excluded subdirectory, no-component package discovery, and wrong-component package discovery, registering configure/build tests with fixture dependencies.

State and persistence: Generates temporary test projects and build trees under `WORK_DIR`, and an install tree under `test_install` for package-discovery tests.

Dependencies and integration points: Integrates puff targets with CTest, the top-level zlib build when embedded, and installed package configs. Runtime tests depend on `tester.cmake`, `tester-cov.cmake`, `pufftest.c`, `puff.c`, `puff.h`, and `zeros.raw`.

Risks: Runtime executable tests are skipped on Windows due to `NOT WIN32`. No-component find-package is expected to fail when not both shared and static libraries are built, making test outcome configuration-sensitive. Generator platform handling stores `-A ${GENERATOR}` as one list item, which can be fragile for some CMake command parsing.

Test signals: Provides the primary test matrix for puff: shared/static linking, package import, subdirectory use, excluded-from-all use, unsupported components, and coverage-specific malformed DEFLATE inputs.
