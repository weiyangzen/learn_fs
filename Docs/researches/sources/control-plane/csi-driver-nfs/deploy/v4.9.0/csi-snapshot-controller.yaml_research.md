<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external snapshot-controller for the v4.9.0 manifest set. It reconciles CSI snapshot Kubernetes resources independently of the NFS controller pod.

## Important APIs, Types, and Functions
The file defines an `apps/v1` `Deployment` named `snapshot-controller`, two replicas, image `snapshot-controller:v8.0.1`, service account `snapshot-controller`, leader election enabled in `kube-system`, and `system-cluster-critical` priority.

## Control Flow, State, and Persistence
Leader election chooses one active reconciler while two replicas provide availability. The controller watches and updates snapshot CRD objects, with `minReadySeconds: 15` guarding against early readiness when v1 CRDs are unavailable.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, control-plane scheduling tolerations, and CSI snapshotter sidecars in driver controller pods.

## Risks and Test Signals
Risks include missing CRDs, RBAC denials, leader election failures, and scheduling failures on tainted control-plane nodes. Signals include available replicas, lease ownership, no CRD discovery errors, and successful `VolumeSnapshot` status reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml -->
