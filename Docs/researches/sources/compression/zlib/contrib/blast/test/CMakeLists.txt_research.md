# sources/compression/zlib/contrib/blast/test/CMakeLists.txt

Purpose: CTest harness for blast runtime tests and CMake package-consumption scenarios.

Important APIs/functions: defines `blast_findTestEnv`, configures five CMake consumer templates, and registers configure/build tests for `find_package`, `add_subdirectory`, `EXCLUDE_FROM_ALL`, no-components, and wrong-components cases.

Control flow: if install testing is enabled and the project is standalone, first installs blast into a test prefix. It configures consumer projects into `WORK_DIR`, runs CMake configure/build tests with the active generator/compiler/platform, marks fixture dependencies, and sets expected failure for wrong components and no-components when not both library kinds are built. It also builds shared/static `blast-test` executables and runs them through `tester.cmake`.

State and persistence: creates multiple test source and build directories under `WORK_DIR`, optional `test_install`, and transient `output.txt` from runtime tests.

Dependencies and integration: relies on `BLAST::BLAST`/`BLAST::BLASTSTATIC` targets, installed package exports, CTest fixtures, and CMake generator expressions. Windows-like shared tests get PATH updated for DLL lookup.

Risks: tests are complex and generator-sensitive; passing `-DCMAKE_BUILD_TYPE=$<CONFIG>` to single-config generators can produce odd values under some CTest contexts. Environment function casing is inconsistent but CMake tolerates command names case-insensitively.

Test signals: validates runtime decompression, standalone install exports, component selection, add_subdirectory use, and expected package failure paths.
