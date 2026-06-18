# sources/compression/zlib/contrib/iostream3/test/CMakeLists.txt

Purpose: defines CTest coverage for iostream3 direct execution, installation, and consumer project integration.

Important APIs/types/functions: test fixture `iostream3_install`, helper function `iostreamv3_findTestEnv`, `configure_file()` calls for consumer templates, configure/build tests for find-package and add-subdirectory modes, shared/static executable tests, and cleanup test.

Control flow: when install testing is enabled, it optionally installs the package to a test prefix, configures multiple generated consumer projects, builds those that should succeed, and marks wrong-component or no-components cases as expected failures when applicable. It then builds/runs direct shared and static test executables from `test.cc`, with PATH adjusted on Windows-like platforms, and removes generated gzip files during fixture cleanup.

State and persistence: writes generated CMake consumer projects and build trees under `WORK_DIR`, installs into `test_install`, and creates temporary gzip output files.

Dependencies/integration: depends on parent variables, CTest fixtures, CMake generator/platform propagation, installed package config files, and zlib imported targets.

Risks: `WORK_DIR` and `inst_setup` are set only in one branch but used by broader install-test logic, so standalone in-tree conditions matter. Some option variable names in templates use `ZLIB_IOSTREAM_BUILD_*` instead of `ZLIB_IOSTREAM3_BUILD_*`. Cleanup ignores missing files unless CMake `-E rm` behavior is acceptable for the version.

Test signals: this file is the main automated test signal for iostream3 packaging and runtime smoke tests.
