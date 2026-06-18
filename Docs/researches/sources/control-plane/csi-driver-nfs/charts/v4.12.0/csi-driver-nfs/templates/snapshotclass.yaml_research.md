# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This small template optionally creates a default-style `VolumeSnapshotClass` for the NFS CSI driver when `volumeSnapshotClass.create` is true.

## APIs, Control Flow, and State
It emits `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, with name from `volumeSnapshotClass.name`, `driver` from `driver.name`, and `deletionPolicy` from `volumeSnapshotClass.deletionPolicy`. It contains no parameters or annotations by default.

## Dependencies and Integration Points
The class depends on snapshot CRDs being present and on the NFS CSI controller snapshotter being enabled to service snapshot requests. User `VolumeSnapshot` objects can reference this class by name.

## Risks and Test Signals
Creating this resource without installed CRDs fails. `deletionPolicy: Delete` can remove underlying snapshot data; `Retain` changes cleanup expectations. Test with `helm template`, dry-run apply, `kubectl get volumesnapshotclass`, and a `VolumeSnapshot` using the class.
