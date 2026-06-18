# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile.go

## Purpose
`reconcile.go` is the top-level reconciliation loop for managed Ceph disruption budgets. It coordinates cluster discovery, pool/RGW/MDS PDB reconciliation, OSD PDB state-machine execution, and cleanup of legacy drain canary resources.

## Important APIs, Types, and Functions
`ReconcileClusterDisruption` holds scheme, controller-runtime client, `controllerconfig.Context`, `ClusterMap`, and maintenance timeout. `Reconcile` wraps `reconcile` with panic recovery. `reconcile` lists CephClusters in the request namespace, updates `ClusterMap`, checks `ManagePodBudgets`, deletes legacy drain canaries once, computes maintenance timeout, calls pool/static PDB processing, computes OSD failure domains, initializes PDB state, and calls `reconcilePDBsForOSDs`. `ClusterMap` provides synchronized namespace-to-cluster storage and lookup. `deleteDrainCanaryPods` removes old drain canary Deployments.

## Control Flow, State, and Persistence
The reconciler requires a namespace. If no CephCluster exists, it does not requeue. If cluster info is not yet populated, it requeues after five seconds. Feature-disabled clusters return without work. Persistent state is primarily Kubernetes PDBs and the PDB state ConfigMap created in OSD logic; `ClusterMap` is in-memory controller state.

## Dependencies and Integration Points
It integrates CephCluster CRs, child pool/object/filesystem CRs, OSD Ceph CLI state, controller-runtime reconcile API, and operator requeue constants.

## Risks
It chooses the first CephCluster in a namespace, relying on the one-cluster-per-namespace model. `deleteLegacyResources` is a package global, so cleanup runs once per process rather than per namespace. In-memory `ClusterMap` is lost on restart but repopulated by reconciliation.

## Test Signals
The subset tests `ClusterMap` behavior. End-to-end reconcile paths are mostly covered indirectly by OSD and pool helper tests.
