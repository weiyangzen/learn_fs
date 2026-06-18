<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml

## Purpose
Defines the v4.13.0 NFS CSI `VolumeSnapshotClass`.

## Important APIs, Types, And Objects
The class is named `csi-nfs-snapclass`, uses driver `nfs.csi.k8s.io`, and sets `deletionPolicy: Delete`.

## Control Flow
`VolumeSnapshot` objects select this class to route snapshot operations to the NFS CSI driver through the snapshot controller and CSI snapshotter.

## State And Persistence Behavior
The class persists as cluster configuration and controls deletion behavior for content created through it. Per-snapshot state lives in `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Dependencies And Integration Points
Depends on snapshot CRDs, the v8.4.0 snapshot controller/sidecar stack, and NFS CSI driver identity matching `nfs.csi.k8s.io`.

## Risks And Edge Cases
Delete policy can remove backing snapshots when Kubernetes snapshot content is deleted. No parameters are set, so all behavior beyond deletion policy is driver default behavior.

## Test Signals
Create, restore, and delete a snapshot with this class; verify content driver, ready status, and backend deletion semantics under v4.13.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml -->
