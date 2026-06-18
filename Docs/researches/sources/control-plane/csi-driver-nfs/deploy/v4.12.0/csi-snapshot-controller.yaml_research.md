<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external CSI snapshot controller in `kube-system` for the v4.12.0 manifest set. It provides the cluster-level control loop that binds `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Important APIs, Types, And Objects
The Deployment runs two replicas of `registry.k8s.io/sig-storage/snapshot-controller:v8.3.0` with `--leader-election=true` and leader election in `$(POD_NAMESPACE)`. It has `minReadySeconds: 15`, rolling update settings of `maxSurge: 0` and `maxUnavailable: 1`, Linux node selection, cluster-critical priority, runtime-default seccomp, and control-plane tolerations.

## Control Flow
After the snapshot CRDs exist, the controller watches snapshot API objects and drives binding, status, and content lifecycle. Only the elected replica actively reconciles. The controller coordinates with CSI snapshotter sidecars, which perform CSI calls against specific drivers such as `nfs.csi.k8s.io`.

## State And Persistence Behavior
The controller persists progress by updating Kubernetes snapshot resources and status subresources. Leader election state is stored in Leases. The Deployment pods have no durable local storage.

## Dependencies And Integration Points
Requires `crd-csi-snapshot.yaml` and `rbac-snapshot-controller.yaml`. It integrates with `VolumeSnapshotClass` resources, `VolumeSnapshot` requests, `VolumeSnapshotContent` binding, and the per-driver snapshotter sidecar in `csi-nfs-controller.yaml`.

## Risks And Edge Cases
If CRDs are missing, comments note the controller may fail readiness or exit quickly, so rollout order matters. Two replicas require correct RBAC for leader election. Because this is a shared cluster controller, changing it can affect snapshots for all CSI drivers, not just NFS.

## Test Signals
Check deployment availability, leader-election Lease updates, and events on snapshot objects. Create a PVC snapshot and confirm `VolumeSnapshotContent` creation, bound status, `readyToUse`, and deletion behavior according to the class policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml -->
