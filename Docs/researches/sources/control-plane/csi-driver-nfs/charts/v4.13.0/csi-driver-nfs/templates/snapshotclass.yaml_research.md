# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally creates the 4.13.0 NFS `VolumeSnapshotClass`.

## APIs, Control Flow, and State
When `volumeSnapshotClass.create` is true it emits a cluster-scoped `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` with name, driver, and deletion policy from values. The template has no parameters, labels, or annotations beyond those fields.

## Dependencies and Integration Points
It depends on snapshot CRDs and the NFS snapshotter path. The class driver must match `driver.name`, which defaults to `nfs.csi.k8s.io`.

## Risks and Test Signals
Wrong deletion policy has data-retention consequences. Test rendering, dry-run apply, and snapshot creation using the class. The template is unchanged from 4.12.x.
