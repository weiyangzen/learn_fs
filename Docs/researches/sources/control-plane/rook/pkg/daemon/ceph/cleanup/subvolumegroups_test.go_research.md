<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go

Purpose: unit tests for CephFS subvolume group cleanup and OMAP-name derivation.

Important APIs/types/functions: `TestSubVolumeGroupCleanup` and `TestGetOmapValue` use mocked command execution with timeout and fixture JSON for subvolumes, snapshots, and pending clones.

Control flow: tests cover an empty subvolume group and a group with one CSI-named subvolume, OMAP lookup/deletion, snapshot listing, pending clone cancellation, snapshot deletion, and forced subvolume removal. `TestGetOmapValue` verifies valid CSI name parsing and invalid-name rejection.

State and persistence behavior: all Ceph commands are mocked; no CephFS or RADOS state is changed.

Dependencies and integration points: depends on Ceph client wrappers invoked by cleanup code, `clusterd.Context`, exec test mocks, and testify assertions.

Risks: error paths, multiple subvolumes/snapshots, malformed command output, and partial cleanup rollback are not covered. The test fixtures pin the expected CSI naming convention.

Test signals: good coverage of expected command ordering and argument shape for the successful cleanup path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go -->
