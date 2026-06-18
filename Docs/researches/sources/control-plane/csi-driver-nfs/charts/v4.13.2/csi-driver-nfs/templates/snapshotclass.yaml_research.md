# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally creates a cluster `VolumeSnapshotClass` for the v4.13.2 NFS CSI driver.

## Important APIs, Types, and Functions
It emits `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` when `volumeSnapshotClass.create` is true. It binds the class to `.Values.driver.name` and applies `.Values.volumeSnapshotClass.deletionPolicy`.

## Control Flow, State, and Persistence
The object is cluster-scoped and has no namespace. Its deletion policy is persisted and copied into dynamically created snapshot content behavior.

## Dependencies and Integration Points
It requires installed snapshot CRDs, a running snapshot controller, and the controller-side CSI snapshotter sidecar. Users reference the class from `VolumeSnapshot.spec.volumeSnapshotClassName`.

## Risks and Test Signals
Risks include CRD absence, driver-name mismatch, and unexpected deletion/retention semantics. Signals include dry-run validation, class listing, and a snapshot using the class reaching ready state.
