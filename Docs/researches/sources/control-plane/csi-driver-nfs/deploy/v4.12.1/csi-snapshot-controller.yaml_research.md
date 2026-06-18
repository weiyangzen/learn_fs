<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml

## Purpose
Deploys the shared external snapshot controller for the v4.12.1 NFS CSI bundle.

## Important APIs, Types, And Objects
The Deployment runs two replicas of `snapshot-controller:v8.3.0` in `kube-system`, using service account `snapshot-controller`, leader election, Linux node selection, cluster-critical priority, and runtime-default seccomp. Readiness is delayed by `minReadySeconds: 15`.

## Control Flow
Once CRDs are available, the elected controller reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects. It updates status and binding state while per-driver snapshotter sidecars invoke CSI snapshot RPCs.

## State And Persistence Behavior
Snapshot state is persisted in Kubernetes custom resources and status subresources. Leader election uses Leases. Pods do not mount durable local storage.

## Dependencies And Integration Points
Requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and snapshot sidecars in CSI driver controller deployments. For NFS, it connects indirectly through `csi-snapshotter:v8.3.0` in the v4.12.1 controller Deployment.

## Risks And Edge Cases
CRD rollout order is critical. As a shared controller, version or RBAC mistakes can affect snapshots cluster-wide. Two replicas depend on Lease permissions and apiserver availability for failover.

## Test Signals
Validate rollout, leader-election Lease churn during pod restart, dynamic snapshot creation, pre-provisioned content binding, status updates, and deletion policy behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml -->
