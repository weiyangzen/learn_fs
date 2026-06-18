# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This small template optionally creates a `VolumeSnapshotClass` for the NFS CSI driver, allowing users to request snapshots without supplying their own class manifest.

## Important APIs, Types, and Functions
It emits `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` when `volumeSnapshotClass.create` is true. The class name comes from `.Values.volumeSnapshotClass.name`, `driver` comes from `.Values.driver.name`, and `deletionPolicy` comes from `.Values.volumeSnapshotClass.deletionPolicy`.

## Control Flow, State, and Persistence
The resource is cluster-scoped and persists independently of namespaces. Its deletion policy controls whether `VolumeSnapshotContent` and backing snapshot data are deleted or retained when bound snapshots are removed.

## Dependencies and Integration Points
It requires snapshot CRDs and a matching CSI driver name. It is consumed by user `VolumeSnapshot` objects and reconciled by the snapshot controller plus the NFS CSI snapshotter sidecar.

## Risks and Test Signals
Risks are creating the class before CRDs exist, using a deletion policy that conflicts with retention expectations, and driver-name mismatches. Signals include `helm template` with class creation enabled, `kubectl get volumesnapshotclass`, and a test snapshot using this class.
