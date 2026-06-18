# sources/compression/zlib/contrib/zlib1-dll/test/CMakeLists.txt

Purpose: CTest suite for zlib1-dll CMake packaging and source embedding.

Important APIs, types, and functions: Uses standalone install fixture, `configure_file` for consumer project templates, generator/platform propagation, `add_test`, and `set_tests_properties`. Key tests cover find-package configure/build, add-subdirectory configure/build, and add-subdirectory with `EXCLUDE_FROM_ALL`.

Control flow: Standalone builds first install zlib1-dll into a private prefix. The script configures three consumer projects and then registers configure and build tests for each, using fixtures to order install/configure/build phases.

State and persistence: Creates generated project directories, build directories, and a private install prefix under `WORK_DIR`.

Dependencies and integration points: Depends on parent `zlib1-dll` targets, `ZLIB1DLLConfig.cmake`, exported targets, and minizip example source lists in the templates.

Risks: Tests always pass `--fresh`, requiring CMake versions that support it; this file itself has no version guard around that flag. Fixture names are reused for multiple configure tests, which is acceptable but can make dependency graphs harder to inspect.

Test signals: Confirms installed package import and in-tree target aliases can link minizip-based consumers against both `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.
