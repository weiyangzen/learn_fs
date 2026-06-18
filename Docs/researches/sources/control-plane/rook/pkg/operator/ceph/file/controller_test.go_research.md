# sources/control-plane/rook/pkg/operator/ceph/file/controller_test.go

## Purpose
This test file exercises the `CephFilesystem` reconciler around cluster readiness, successful filesystem reconciliation, deletion blocking by dependents, and MDS CephX key rotation status. It uses fake Kubernetes clients and mock Ceph executors to validate controller behavior without a real Ceph cluster.

## Important APIs, Types, and Functions
`TestCephFilesystemController` covers missing cluster, unready cluster, successful ready-cluster reconciliation, and deletion blocked by a mocked `CephFilesystemDependents`. `TestMdsKeyRotation` covers first reconcile CephX status, repeated reconcile stability, brownfield unknown status preservation, transition from unknown to known during rotation, and additional generation-based rotations. The tests override `currentAndDesiredCephVersion`, `mds.UpdateDeploymentAndWait`, and executor command outputs.

## Control Flow, State, and Persistence
The tests construct `CephFilesystem`, `CephCluster`, monitor Secret, fake controller-runtime client, fake typed clientset, and a `ReconcileCephFilesystem`. Command responses simulate `ceph status`, `ceph fs get`, `ceph auth get-or-create-key`, `ceph auth rotate`, and `ceph versions`. Successful reconcile verifies `Status.Phase == Ready`. The deletion-block test gives the filesystem a deletion timestamp and replaces the dependency function to force a dependent event. The key-rotation test mutates the cluster CephX daemon policy and verifies CR status and generated keyring Secret data across several reconciles.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, controller-runtime fake clients, Rook API schemes, mock executor utilities, fake event recorders, `mds` deployment update stubs, keyring Secret creation, and Ceph version constants. It is a high-level integration test across controller, filesystem creation, MDS deployment/keyring generation, and status updating.

## Risks
The test suite mutates package-level functions and relies on deferred restoration only in some subtests, so future parallelization would be unsafe. Mock executor matching is argument-position based and may hide unasserted command changes by returning empty success for unmatched cases in some blocks. The deletion test mocks dependency discovery instead of exercising the real Ceph subvolume checks. The ready path does not validate all Kubernetes resources produced by MDS deployment generation.

## Test Signals
Signals include requeue results when the cluster is absent/unready, Ready status after successful reconcile, event content when deletion is blocked, CephX key generation/version persistence, Secret keyring updates on rotation, and absence of further Secret updates when the configured generation is already satisfied.
