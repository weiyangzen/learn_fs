<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go

Purpose: unit tests for host-path cleanup helpers.

Important APIs/types/functions: `Test_cleanCSIDirs`, `Test_cleanExporterDir`, `Test_monDir`, and `Test_secretKeyMatch` use temporary directories and real filesystem operations.

Control flow: tests create CSI, exporter, and monitor/keyring directories under `t.TempDir`, invoke cleanup helpers, and assert expected deletion or retention. `Test_secretKeyMatch` checks both matching and mismatching extracted keys.

State and persistence behavior: all state is temporary filesystem state owned by the test process. No Kubernetes or Ceph cluster is contacted.

Dependencies and integration points: tests production cleanup helpers, Go `os`/`filepath`, and testify assertions.

Risks: `Test_cleanCSIDirs` appears to assert the RBD path twice and does not independently assert the CephFS CSI path after cleanup. Broader `StartHostPathCleanup` and error branches are not covered.

Test signals: protects key deletion safety for monitor directories and basic recursive deletion of exporter/CSI paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go -->
