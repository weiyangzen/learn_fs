# sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_exclude_test.cmake.in

Purpose: Consumer-project template verifying `zlib1-dll` works when added as an excluded subdirectory.

Important APIs, types, and functions: Calls `add_subdirectory(@zlib1-dll_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, defines minizip example sources including conditional `iowin32.c`, creates `test_example` and `test_example_wapi`, and links them to `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: Configure embeds the zlib1-dll project without adding its default targets to `all`, then explicitly builds consumer executables that force the needed DLL targets through link dependencies.

State and persistence: Affects only generated build-tree targets.

Dependencies and integration points: Integrates zlib1-dll with minizip sources and verifies both exported aliases in an embedded build.

Risks: Uses `${WIN32}` inside a generator expression in configured content, so the generated project's platform semantics matter. The test compiles minizip CLI source rather than a minimal symbol check.

Test signals: Parent CTest configures and builds this project to validate excluded-subdirectory consumption.
