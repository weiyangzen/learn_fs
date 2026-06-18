# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Main.cc

Purpose: GTest entry point for `eos-ns-quarkdb-tests`.
Important APIs/types/functions: `main(int argc,char** argv)` initializes a fixed scratch path, calls `testing::InitGoogleTest`, then `RUN_ALL_TESTS()`.
Control flow: removes `/tmp/eos-ns-tests/`, recreates it with mode `0755`, initializes GoogleTest, and runs the full test binary.
State/persistence: clears local queue/scratch state before tests; QDB state is flushed by `NsTests` fixture construction, not here.
Dependencies/integration: includes GTest and `MetadataFlusher.hh`; uses POSIX `mkdir` and `system("rm -rf ...")`.
Risks: hard-coded `/tmp/eos-ns-tests/` and shell `rm -rf` are destructive within that path; no error checks for removal or directory creation; parallel test binaries would share the same scratch directory.
Test signals: provides deterministic local filesystem setup for the active test suite.
