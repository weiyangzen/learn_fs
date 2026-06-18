<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml

## Purpose
Defines the v4.12.1 `VolumeSnapshotClass` for the NFS CSI driver.

## Important APIs, Types, And Objects
The object is `snapshot.storage.k8s.io/v1`, named `csi-nfs-snapclass`, with `driver: nfs.csi.k8s.io` and `deletionPolicy: Delete`.

## Control Flow
Snapshot requests reference this class to select the NFS CSI snapshotter path. The snapshot controller binds the request and the sidecar calls the NFS CSI controller.

## State And Persistence Behavior
The class persists cluster-wide and influences future snapshot content deletion behavior. It stores configuration only, not per-snapshot status.

## Dependencies And Integration Points
Requires snapshot CRDs/controllers and a matching NFS CSI driver identity. It pairs with the v4.12.1 controller sidecar `csi-snapshotter:v8.3.0`.

## Risks And Edge Cases
The delete policy can remove backend snapshots when snapshot content is deleted. No parameters are set, so there is no manifest-level override for backend-specific snapshot behavior.

## Test Signals
Create and delete a snapshot using this class, then verify content driver fields, ready status, restore behavior, and backend cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml -->
