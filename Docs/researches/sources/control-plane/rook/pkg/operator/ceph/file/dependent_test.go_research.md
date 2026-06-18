# sources/control-plane/rook/pkg/operator/ceph/file/dependent_test.go

## Purpose
This test suite validates `CephFilesystemDependents` across Kubernetes subvolume group CRs, Ceph subvolume group contents, ignored internal groups, no-group subvolumes, and error aggregation.

## Important APIs, Types, and Functions
`TestCephFilesystemDependents` overrides `client.GetFilesystem`, `client.ListSubvolumeGroups`, and `client.ListSubvolumesInGroup`. It uses fake Rook clientsets to create `CephFilesystemSubVolumeGroup` resources and verifies `DependentList.Empty`, `PluralKinds`, and `OfKind`. Test helpers model missing and existing Ceph filesystems plus empty and non-empty subvolume lists.

## Control Flow, State, and Persistence
Each subtest sets mocked Ceph client functions, builds a `clusterd.Context`, optionally creates typed CRs, calls `CephFilesystemDependents`, and checks the resulting dependent categories/names. The mock functions assert that the filesystem name is propagated correctly and panic on unexpected group names to catch new control-flow paths. State is isolated in in-memory fake clients and restored mock functions via defer.

## Dependencies and Integration Points
The tests depend on Rook API types, fake versioned clientsets, Ceph client function variables, `client.AdminTestClusterInfo`, and `testify/assert`. They validate integration between Ceph-side dependency checks and Kubernetes CR-side dependency checks.

## Risks
The helper `newClusterdCtx` accepts objects but ignores them, so setup depends on explicit clientset creates inside each subtest. Mocking `GetFilesystem` with `syscall.Errno(2)` exercises the intended ENOENT path but not every possible command-error wrapper. Tests run serially because they mutate global Ceph client functions.

## Test Signals
Signals include no dependents for missing filesystems, no dependents for empty groups, blocking on matching `CephFilesystemSubVolumeGroup`, blocking on non-empty `csi` group, combined dependency categories, error text for failed subvolume listing, skipping `_index`, `_legacy`, `_deleting`, and explicit `<no group>` reporting when subvolumes are outside any group.
