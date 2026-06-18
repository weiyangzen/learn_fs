# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash_test.go

## Purpose
This file tests crash collector Deployment generation for node daemons.

## Important APIs, Types, And Functions
`TestGenerateCrashEnvVar` validates `CEPH_ARGS` for `ceph-crash`. `TestCreateOrUpdateCephCrash` constructs a fake `ReconcileNode`, fake scheme/client, a node with hostname label, tolerations, a CephCluster, and a Ceph version, then calls `createOrUpdateCephCrash()`.

## Control Flow And State
The test first creates a crash collector Deployment and verifies operation result `created`, node selector, tolerations, host network false, no priority class, and Ceph user security context. It then mutates cluster labels, host network, priority class, and tolerations, calls the function again, and verifies operation result `updated` plus changed pod labels, host network, priority class, and Rook version label placement on the Deployment but not the pod template.

## Dependencies And Integration Points
The test depends on controller-runtime fake client, Rook fake clientsets, the Rook scheme, Kubernetes Deployment/Node types, and Ceph API priority/label specs. It validates the object mutation path used during node reconciliation.

## Risks And Test Signals
The test catches regressions in selector/label construction, host-network propagation, toleration propagation, and security context expectations. It does not test missing hostname label or actual `ceph-crash` execution.
