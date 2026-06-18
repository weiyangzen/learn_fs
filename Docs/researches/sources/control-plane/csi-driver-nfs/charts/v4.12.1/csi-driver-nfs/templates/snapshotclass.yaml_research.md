# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally emits a `VolumeSnapshotClass` for NFS CSI snapshots in chart 4.12.1.

## APIs, Control Flow, and State
When `volumeSnapshotClass.create` is true, it renders a `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named from values, with `driver` set to the CSI driver name and `deletionPolicy` from values. It does not persist namespaced state and has no Helm logic beyond the create guard.

## Dependencies and Integration Points
The resource depends on installed snapshot CRDs and is consumed by user `VolumeSnapshot` resources plus the snapshot controller/sidecars. It is unchanged from 4.12.0.

## Risks and Test Signals
Wrong driver names prevent the class from matching the CSI driver; deletion policy controls physical snapshot retention. Test with dry-run apply and a snapshot using this class.
