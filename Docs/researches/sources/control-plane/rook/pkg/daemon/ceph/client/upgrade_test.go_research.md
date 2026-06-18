# sources/control-plane/rook/pkg/daemon/ceph/client/upgrade_test.go

This test file validates upgrade helpers, especially command wiring and edge-case decisions for OSD and version handling.

Tests assert `ceph version`, `ceph versions`, and `ceph osd require-osd-release` command construction. `TestOkToStopDaemon` checks daemon ok-to-stop calls and no-error behavior. `TestOkToContinue` verifies non-MDS daemon types do not run extra checks. `TestFindFSName`, `TestDaemonMapEntry`, and `TestBuildHostListFromTree` cover pure helper parsing. `TestGetRetryConfig` documents default, OSD, and MDS retry/delay values.

`TestOSDUpdateShouldCheckOkToStop` uses fake OSD list/tree output to show that fewer than three OSDs skips checks, while three or more OSDs generally checks. `TestLeastUptodateDaemonVersion` loops 100 times over a versions map to ensure the least version is selected deterministically despite random map iteration.

State is mocked Ceph output only. Integration points include fake OSD output helpers, Ceph version parsing, and executor mocks. Gaps include full `OkToStop()` retry behavior, all-in-one OSD bypass through `osdDoNothing()`, MDS status retry, and real Ceph errors beyond induced mock failures.
