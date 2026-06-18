# sources/distributed-fs/lizardfs/src/unittests/CMakeLists.txt

Purpose: Build configuration for the shared `mfsunittests` support library.

Important APIs/types/functions: `collect_sources(UNITTESTS)`; `add_library(mfsunittests ${UNITTESTS_SOURCES})`.

Control flow: CMake collects unittest support sources and builds them into a library consumed by test binaries.

State and persistence: Build-system state only.

Dependencies and integration: Integrates helper sources such as packet helpers, constants, plan tester, and mocks into the test build.

Risks and test signals: Missing files from source collection can break downstream tests. No runtime behavior.
