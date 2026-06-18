<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml

## Purpose
Deploys snapshot-controller v8.0.1 for CSI snapshot API reconciliation in clusters using the v4.8.0 NFS driver manifests.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` named `snapshot-controller` runs two replicas in `kube-system`, uses service account `snapshot-controller`, enables leader election in `kube-system`, and uses image `registry.k8s.io/sig-storage/snapshot-controller:v8.0.1`.

## Control Flow, State, and Persistence
The deployment uses rolling updates with no surge and one unavailable replica, plus `minReadySeconds: 15` so CRD discovery failures surface before readiness. State lives in snapshot CRDs and leader-election leases rather than local storage.

## Dependencies and Integration Points
It depends on snapshot CRDs from `crd-csi-snapshot.yaml` and permissions from `rbac-snapshot-controller.yaml`. It coordinates with NFS controller `csi-snapshotter` sidecar operations for creating and deleting CSI snapshots.

## Risks and Test Signals
Risks include CRDs not installed before startup, RBAC gaps, control-plane scheduling restrictions, and leader election problems. Signals are available replicas, current lease ownership, no CRD discovery errors, and snapshots reaching ready status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml -->
