<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go

## Purpose
`rbd_util_test.go` provides unit coverage for pure or local helper behavior in `rbd_util.go`.

## Important APIs, Types, And Functions
Tests include `TestHasSnapshotFeature`, `TestValidateImageFeatures`, `TestGetCephClientLogFileName`, `TestStrategicActionOnLogFile`, `TestIsKrbdFeatureSupported`, `Test_checkValidImageFeatures`, and `Test_shouldRetryVolumeGeneration`.

## Control Flow
The tests build `rbdVolume` values with feature sets and mounters, assert validation errors for missing dependencies and NBD-required journaling, create temporary log files to verify remove/compress/preserve behavior, initialize `krbdFeatures` for feature support checks, and verify retry classification for known errors.

## State And Persistence
Filesystem effects are limited to temporary log files and gzip output under `t.TempDir()`. The package-level `krbdFeatures` variable is mutated in parallel subtests, which is a test-global side effect.

## Dependencies And Integration Points
The tests depend on go-ceph RBD feature parsing and errors, RADOS permission errors, Ceph-CSI internal errors, util sentinel errors, and `testify/require`.

## Risks
The tests avoid real Ceph connections. Parallel tests mutating package-level `krbdFeatures` could become flaky if additional tests assume a different value concurrently. The file does not cover JSON stash, image deletion, RBD metadata migration, or volume ID generation.

## Test Signals
Good signal for feature validation and local log policy; weak signal for backend behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go -->
