# sources/control-plane/rook/pkg/daemon/ceph/client/status_test.go

This test file verifies the status JSON model and health helper decisions. It uses static Ceph status JSON and direct helper calls to avoid a live cluster.

`TestStatusMarshal` unmarshals a Luminous-era `ceph status -f json` fixture and checks health checks, monitor map fields, OSD map counts, near-full state, and PG map counters. `TestIsClusterClean` builds synthetic PG states to check that all PGs must match the healthy regex and sum to `NumPgs`; it also verifies custom regex behavior does not accidentally mark mixed states clean. `TestGetMDSRank` parses a Nautilus-style fsmap fixture and asserts rank lookup. `TestIsCephHealthy` confirms `HEALTH_WARN` and `HEALTH_OK` are accepted and `HEALTH_ERR` is rejected. `TestMuteHealthWarning` ensures the command is built as `ceph health mute <warning> --sticky` and that command failure is logged rather than propagated.

The test signal is strongest for JSON compatibility and pure helper behavior. It does not exercise live command execution, custom regex compile errors, or all MDS transition branches. It documents that warning health is considered good enough for certain upgrade checks.
