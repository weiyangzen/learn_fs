# sources/control-plane/rook/pkg/operator/ceph/csi/controller.go

## Purpose
`controller.go` defines the CSI controller reconciler that reacts to operator config and CephCluster events, initializes CSI shared config, applies operator settings, derives driver names, and prepares ceph-csi-operator mapping state.

## Important APIs, Types, and Functions
`ReconcileCSI` stores scheme, controller-runtime client, `clusterd.Context`, operator context/config, and the first cluster spec. `Add`, `newReconciler`, and `add` register the controller, CSIAddons scheme, ConfigMap watch, CephCluster watch, and ceph-csi-operator scheme. `Reconcile` wraps `reconcile` with panic recovery. `reconcile` creates the CSI ConfigMap, applies operator settings, derives `CephFSDriverName`, `RBDDriverName`, and `NFSDriverName`, lists CephClusters, creates an empty peer-map config, and loads cluster info for ready clusters.

## Control Flow, State, and Persistence
On each reconcile, the controller obtains an operator deployment owner reference, ensures `rook-ceph-csi-config`, applies operator settings from ConfigMap/env, then lists all CephClusters. If none exist, it exits. For existing clusters it skips deleting/cleanup-policy clusters, stores the first spec, loads cluster info, and sets owner info. State persists in Kubernetes ConfigMaps and package-level driver name globals.

## Dependencies and Integration Points
It integrates with controller-runtime watches/predicates, CSIAddons API, ceph-csi-operator API, Rook operator settings, cluster info loading, and peer-map config creation.

## Risks
Package-level driver name mutation affects all clusters and tests. The reconciler returns early if any cluster is deleting or has cleanup policy, which can skip later clusters. Cluster info load failures can either requeue or abort depending on type. The file currently prepares cluster info but does not itself call the CephConnection/Profile creation helpers.

## Test Signals
Tests validate no-cluster and basic cluster-present reconciliation. Broader signals would verify watch setup, peer-map creation, multi-cluster iteration behavior, and driver-name globals.
