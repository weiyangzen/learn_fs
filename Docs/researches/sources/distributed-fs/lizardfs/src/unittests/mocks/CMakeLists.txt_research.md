# sources/distributed-fs/lizardfs/src/unittests/mocks/CMakeLists.txt

Purpose: Build configuration for the `mfsunittests-mocks` library.

Important APIs/types/functions: `collect_sources(UNITTESTS_MOCKS)`; `add_library(mfsunittests-mocks ${UNITTESTS_MOCKS_SOURCES})`.

Control flow: CMake collects mock sources and packages them into a library for tests.

State and persistence: Build-system state only.

Dependencies and integration: Supplies `ModuleMock`, `ChunkConnectorMock`, and related mock tests to the test build.

Risks and test signals: Source collection must include both mock implementations and any mock-specific tests expected by the build.
