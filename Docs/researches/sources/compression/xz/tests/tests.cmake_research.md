# sources/compression/xz/tests/tests.cmake

Purpose: optional CMake test harness for XZ Utils. It builds liblzma unit-test executables and registers command-line shell tests without letting the `tests` directory affect ordinary builds when excluded.

Important APIs/functions: uses CMake `include(CTest)`, `add_library(OBJECT)`, `add_executable`, `target_include_directories`, `target_link_libraries`, `add_test`, `set_tests_properties`, and feature variables such as `XZ_ENCODERS`, `XZ_DECODERS`, `SUPPORTED_FILTERS`, `SUPPORTED_CHECKS`, `XZ_CHECKS`, `ENABLE_SCRIPTS`, and `XZ_LZIP_DECODER`.

Control flow: when `BUILD_TESTING` is on, creates `tests_w32res` for Windows manifests, defines the `LIBLZMA_TESTS` list, conditionally appends `test_microlzma`, builds each test into `tests_bin`, and registers it with `srcdir` and skip code 77. It computes whether all encoders, decoders, and checks are enabled, then conditionally registers shell tests for scripts, suffixes, compression vectors, and file decompression.

State and persistence: emits test binaries under `${CMAKE_CURRENT_BINARY_DIR}/tests_bin` and scratch directories for shell tests. It does not persist runtime state beyond build artifacts and CTest metadata.

Dependencies and integration: depends on the main CMake build creating `liblzma`, source include directories, feature variables, and optional Windows resource dependencies. It integrates with CTest and mirrors Autotools skip semantics.

Risks: feature gating is necessarily approximate for shell scripts because CMake builds lack `config.h`. Shell tests are Unix-only. Windows manifest object generation uses a header-only dummy source and explicit linker language to satisfy CMake/Ninja.

Test signals: CTest names correspond to test programs or scripts. `SKIP_RETURN_CODE 77` is set consistently so disabled features do not become failures.
