# sources/control-plane/rook/pkg/daemon/ceph/osd/remove_test.go

## Purpose
`remove_test.go` verifies that PVC cleanup for PVC-backed OSD removal selects all PVCs belonging to the same device set and set index, while leaving other OSD PVCs in the set untouched.

## Important APIs, Types, and Functions
`TestRemovePVCs()` drives the private `removePVCs()` helper. `createTestPVCs()` creates test PVCs by instantiating the operator OSD cluster object and calling `PrepareStorageClassDeviceSets()`. `testVolumeClaim()` constructs minimal `VolumeClaimTemplate` values.

## Control Flow
The test installs a fake Kubernetes reactor that fills `GenerateName` PVC names deterministically. The first subtest creates a two-count device set with only a data PVC template, verifies two PVCs exist, calls `removePVCs()` for the first OSD's data PVC, and asserts only the second OSD's PVC remains. The second subtest creates data, metadata, and wal templates for two OSDs, verifies six PVCs, calls `removePVCs()` for one data PVC, and asserts all three PVCs for set index `0` are deleted while the other three remain.

## State and Persistence
State is entirely fake Kubernetes PVC state. The generated names and labels are created through real operator preparation logic, so the test validates compatibility between operator PVC labeling and daemon cleanup selection.

## Dependencies and Integration Points
The test integrates daemon removal code with operator OSD PVC creation code, fake Kubernetes client reactors, storage class device set specs, and OSD label constants. This is useful because `removePVCs()` depends on labels set by a different package.

## Risks
Only the delete path is tested. The `preservePVC=true` path that detaches labels is not covered. The test does not validate prepare Job deletion or deployment-label discovery, so full `removeOSD()` resource cleanup can regress independently. The reactor mutates create actions in place, which is deliberate but tightly coupled to fake client behavior.

## Test Signals
Good signals are set-index isolation and multi-template PVC deletion. Additional coverage should assert preserve mode removes `CephDeviceSetPVCIDLabelKey` without deleting PVCs, and that missing labels or missing data PVCs fail gracefully.
