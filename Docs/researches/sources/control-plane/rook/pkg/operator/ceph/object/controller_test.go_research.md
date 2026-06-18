# sources/control-plane/rook/pkg/operator/ceph/object/controller_test.go

## Purpose
`controller_test.go` exercises the CephObjectStore reconciler across readiness gates, normal creation, multisite behavior, external stores, secret mapping, version comparison, and cephx key rotation.

## Important APIs, Types, and Functions
The tests build fake controller-runtime clients, fake Rook clientsets, mock Ceph executors, and replace package globals such as `currentAndDesiredCephVersion`, `commitConfigChanges`, and `cephObjectStoreDependents`. Major cases include `TestCephObjectStoreController`, `TestCephObjectStoreControllerMultisite`, `TestCephObjectStoreControllerZoneNotReady`, `TestCephObjectExternalStoreController`, `TestDiffVersions`, `Test_mapSecretToCR`, and `TestKeyRotation`.

## Control Flow, State, and Persistence
The tests simulate CRs, CephCluster readiness, monitor secrets, Ceph command output, multisite JSON, object-store deletion timestamps, and generated Deployments/Secrets. They assert reconcile results, status phases, endpoint info, dependency checks, finalizer behavior, event-free success paths, and keyring secret contents after rotation.

## Dependencies and Integration Points
This suite integrates Rook API schemes, fake Kubernetes clients, mock Ceph command execution, Ceph version parsing, keyring status helpers, status/reporting code, and multisite admin command JSON. It is a high-value regression net for interactions that span Kubernetes objects and Ceph CLI output.

## Risks and Test Signals
Strong signals include requeue on missing/not-ready CephCluster, `Ready` status and endpoint population on success, no RGW start before a multisite zone is Ready, external-store missing-secret requeue, object-store secret watch mapping, and cephx generation tracking. Residual gaps include real controller watch wiring, real Ceph admin command failures, status update conflicts, and concurrent reconciles.
