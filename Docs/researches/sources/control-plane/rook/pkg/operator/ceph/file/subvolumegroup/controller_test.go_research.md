<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go

## Purpose
This test file validates key reconciliation paths and helpers for `CephFilesystemSubVolumeGroup`.

## Important APIs and control flow
`TestFilesystemSubvolumeGroupController` builds fake clients, fake Rook clientsets, and mock Ceph executors. It exercises missing cluster and not-ready cluster requeues, filesystem-not-ready requeue, successful subvolume group creation and pinning, CSI config map creation, external-mode CSI config updates without Ceph subvolume creation, and a Multus cluster path. `Test_buildClusterID` verifies deterministic hashed cluster IDs and explicit `spec.clusterID` override. `Test_formatPinning` verifies default distributed pinning and export/distributed/random rendering.

## State and persistence
The tests persist state only in fake Kubernetes clients and mocked clientsets. They create mock monitor secrets, CSI config maps, and CR status updates in memory. Mock executor responses simulate Ceph status, daemon versions, subvolume group create, and pin commands.

## Dependencies and integration points
The tests register Rook and CSI operator API schemes, use Rook test clientsets, `exectest.MockExecutor`, CSI config helpers, and controller-runtime fake clients. They validate integration among CephCluster readiness, CephFilesystem status, Ceph CLI invocation, and CSI config updates.

## Risks and test signals
The tests cover creation and readiness but not deletion, shared subvolume group reference handling, ENOENT/ENOTEMPTY delete errors, force cleanup jobs, or status conflict retries. Mock command matching is narrow, so changes to Ceph command order or arguments can expose integration regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go -->
