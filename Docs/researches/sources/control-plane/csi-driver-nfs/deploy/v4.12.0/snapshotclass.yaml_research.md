<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml

## Purpose
Defines a `VolumeSnapshotClass` named `csi-nfs-snapclass` for snapshots handled by the NFS CSI driver.

## Important APIs, Types, And Objects
The class uses `apiVersion: snapshot.storage.k8s.io/v1`, `driver: nfs.csi.k8s.io`, and `deletionPolicy: Delete`. It has no parameters, so behavior is entirely driver default behavior plus the delete policy.

## Control Flow
Users reference this class from `VolumeSnapshot.spec.volumeSnapshotClassName`. The snapshot controller and CSI snapshotter use the driver field to route snapshot operations to the NFS CSI controller plugin.

## State And Persistence Behavior
The class is a persistent cluster-scoped configuration object. Snapshot contents created through it inherit deletion behavior, but the class itself does not store snapshot runtime status.

## Dependencies And Integration Points
Requires snapshot CRDs, snapshot controller RBAC/deployment, the CSI snapshotter sidecar, and a driver identity matching `nfs.csi.k8s.io`.

## Risks And Edge Cases
`deletionPolicy: Delete` means deleting the Kubernetes snapshot content is expected to delete the backing snapshot. That is convenient for cleanup but risky for retention workflows. Without parameters, any required backend-specific options must come from driver defaults.

## Test Signals
Create a `VolumeSnapshot` using this class, confirm it binds to a `VolumeSnapshotContent` with driver `nfs.csi.k8s.io`, then delete the snapshot and verify expected backing cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml -->
