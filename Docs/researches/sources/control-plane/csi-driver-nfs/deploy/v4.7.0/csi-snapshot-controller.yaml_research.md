<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external snapshot-controller for CSI snapshot reconciliation in `kube-system`. It is independent of the NFS plugin pod but required for `VolumeSnapshot` and `VolumeSnapshotContent` control loops.

## Important APIs, Types, and Functions
The file defines an `apps/v1` `Deployment` named `snapshot-controller` with two replicas, image `registry.k8s.io/sig-storage/snapshot-controller:v8.0.1`, leader election enabled, and leader election namespace `kube-system`. It uses service account `snapshot-controller` and `system-cluster-critical` priority.

## Control Flow, State, and Persistence
Two replicas are rolled with `maxSurge: 0`, `maxUnavailable: 1`, and `minReadySeconds: 15`, allowing only one active reconciler through leader election. The controller watches snapshot CRDs and persists desired/observed snapshot state through Kubernetes API objects, not local disk. Readiness depends on v1 snapshot CRDs being installed.

## Dependencies and Integration Points
It depends on snapshot CRDs, the RBAC in `rbac-snapshot-controller.yaml`, Kubernetes lease objects for leader election, and CSI snapshotter sidecars running with CSI drivers. It tolerates common control-plane taints so it can run on master/control-plane nodes.

## Risks and Test Signals
Risks include missing CRDs, insufficient snapshot RBAC, leader election namespace issues, and split-brain or downtime if replicas cannot acquire leases. Signals are available deployment replicas, a current leader lease, no CRD discovery errors, and successful reconciliation of `VolumeSnapshot` status fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml -->
