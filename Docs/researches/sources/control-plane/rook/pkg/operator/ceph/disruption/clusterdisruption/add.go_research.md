# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/add.go

## Purpose
`add.go` registers the cluster disruption controller and its watches. The controller manages safe PodDisruptionBudget behavior for Ceph OSDs, RGWs, and MDS daemons.

## Important APIs, Types, and Functions
`objectsToWatch` lists `CephBlockPool`, `CephFilesystem`, and `CephObjectStore`. `cephClusterPredicate` reconciles on CephCluster creates and spec updates. `pdbPredicate` watches the main OSD PDB and reconciles when `DisruptionsAllowed` falls to zero with `maxUnavailable=1`. `watchNamespacedObject` maps namespaced child resource events to a reconcile request for that namespace. `Add` constructs `ReconcileClusterDisruption`, creates the controller, and registers all watches.

## Control Flow, State, and Persistence
Registration creates a shared `ClusterMap` and passes it to the reconciler. Watches enqueue either direct CephCluster requests or namespace-only requests that the reconciler later resolves to the cluster name.

## Dependencies and Integration Points
It integrates controller-runtime controller/watch/source/handler/predicate APIs, Rook Ceph CRDs, Kubernetes PDBs, and `controllerconfig.Context`.

## Risks
Spec comparison uses `reflect.DeepEqual`, so semantically equivalent defaulting changes can trigger reconciliation. Namespace-only requests depend on `ClusterMap` being populated during reconciliation. PDB predicate only watches a narrow transition on the default OSD PDB.

## Test Signals
This file has no direct test in the subset. Behavior is indirectly tested by disruption reconciler tests and would benefit from predicate/watch unit coverage.
