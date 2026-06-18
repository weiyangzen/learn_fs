<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go

## Purpose
This file provides high-level reconciliation tests for the `CephNFS` controller, including lifecycle, scale, multiple CR isolation, image override, security validation, and CephX key rotation.

## Important APIs and control flow
`TestCephNFSController` sets up fake schemes, fake controller clients, mock clientsets, and mock Ceph/RADOS/Ganesha executors. It tests no-cluster and cluster-not-ready requeues, invalid SSSD security validation and event reporting, initial and repeated reconcile for one and three servers, scale-down from three to two and one, two independent CephNFS resources, and custom Ganesha image/pull policy propagation. `TestNFSKeyRotation` stubs Ceph versions and auth responses to verify first reconcile, status retention, brownfield unknown status, key-generation-driven rotation, and no extra rotation. `TestGetGaneshaConfigObject` verifies config object naming.

## State and persistence
All state is fake or mocked: Kubernetes Deployments/Services/ConfigMaps in a test clientset, CR status in a fake controller client, monitor secrets in fake core clientsets, and Ceph/RADOS command behavior from mock executors.

## Dependencies and integration points
The tests depend on Rook fake clientsets, controller-runtime fake clients, fake event recorders, keyring/version hooks, and deployment update stubs. They assert integration across controller status, deployment lifecycle, config maps, services, RADOS command calls, and CephX status.

## Risks and test signals
These tests are broad but still mock away actual RADOS object content, Kubernetes API conflict behavior, and Ceph command semantics. They are strong signals for label selectors, resource naming, scaling, status phase, and CephX generation regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go -->
