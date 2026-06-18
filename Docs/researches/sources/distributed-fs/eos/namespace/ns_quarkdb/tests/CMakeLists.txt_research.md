# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/CMakeLists.txt

Purpose: Builds QuarkDB namespace tests and benchmark executables.
Important APIs/types/functions: `eos-ns-quarkdb-tests` includes service/view/filtering/inode/other test units and links GTest/gmock plus `EosNsCommon-Static` and Folly; `eosnsbench` builds from `EosNamespaceBenchmark.cc`; `eos-lru-benchmark` builds from `LruBenchmark.cc` and links `EosCommon` and CLI11.
Control flow: CMake adds the repository root to includes, declares executables, applies `_FILE_OFFSET_BITS=64` to namespace benchmark, links libraries, and installs test/benchmark binaries.
State/persistence: no runtime state, but comments state the unit tests require a running QuarkDB instance.
Dependencies/integration: integrates the test suite with the broader EOS build and install layout.
Risks: `VariousTests.cc` is referenced here but outside this research item; test success depends on external QDB environment and build-time package availability.
Test signals: this is the build entry point for all active test files in this subset.
