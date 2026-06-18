# sources/control-plane/rook/pkg/operator/ceph/csi/predicate_test.go

## Purpose
This test file verifies CSI controller predicates for operator ConfigMap and CephCluster events.

## Important APIs, Types, and Functions
`Test_cmPredicate` exercises ConfigMap create, delete, and update event filters. `Test_cephClusterPredicate` exercises CephCluster create decisions with fake clients containing or omitting the operator config map and duplicate clusters.

## Control Flow, State, and Persistence
Tests build typed controller-runtime events and call predicate methods directly. CephCluster predicate tests use fake controller-runtime clients and registered schemes to simulate config-map lookup and duplicate cluster listing.

## Dependencies and Integration Points
The tests integrate `corev1.ConfigMap`, `cephv1.CephCluster`, the Rook scheme, controller-runtime fake client, and capnslog debug logging.

## Risks
Update/delete/generic behavior for CephCluster is mostly untested except as code inspection. ConfigMap tests only change `.Data`; they do not cover resource quantity comparison or metadata-only changes.

## Test Signals
Signals confirm non-operator ConfigMaps are ignored, operator config creates/deletes reconcile, data changes reconcile, repeated CephCluster generations are suppressed when a ConfigMap exists, env-only deployments reconcile without the ConfigMap, and duplicate clusters are suppressed.
