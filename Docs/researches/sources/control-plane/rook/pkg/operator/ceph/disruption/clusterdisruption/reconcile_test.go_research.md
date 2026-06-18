# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile_test.go

## Purpose
This test file validates the thread-safe `ClusterMap` helper used by the disruption controller to associate namespaces with CephCluster names.

## Important APIs, Types, and Functions
`TestClusterMap` calls `GetClusterInfo`, `UpdateClusterMap`, and `GetClusterNamespaces` on a shared `ClusterMap`.

## Control Flow, State, and Persistence
The test starts with an empty map, asserts missing lookup returns nil, populates three namespaces, validates a retrieved `ClusterInfo` name/namespace, verifies missing namespace lookup, and checks namespace count. State is in-memory only.

## Dependencies and Integration Points
The test uses `cephv1.CephCluster`, Kubernetes `ObjectMeta`, and testify assertions.

## Risks
The test does not exercise concurrent access despite the mutex-backed implementation. `GetClusterNamespaces` order is not asserted, only length, which is appropriate for map-backed data.

## Test Signals
Signals confirm lazy map initialization, namespace-to-cluster mapping, construction of admin cluster info, missing lookup behavior, and namespace enumeration count.
