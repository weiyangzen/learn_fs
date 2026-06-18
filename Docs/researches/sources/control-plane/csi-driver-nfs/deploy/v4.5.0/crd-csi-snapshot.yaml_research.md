# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/crd-csi-snapshot.yaml

## Purpose
This v4.5.0 manifest installs the same CSI snapshot API CRDs as v4.4.0. It provides cluster-wide `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` API storage for the NFS CSI snapshot components.

## Important APIs, Types, and Functions
The three `CustomResourceDefinition` objects are `volumesnapshots.snapshot.storage.k8s.io`, `volumesnapshotclasses.snapshot.storage.k8s.io`, and `volumesnapshotcontents.snapshot.storage.k8s.io`. They serve `v1` and `v1beta1`, store `v1`, define structural schemas for snapshot sources, classes, CSI drivers, deletion policies, content bindings, restore size, readiness, error status, and expose status subresources and kubectl printer columns.

## Control Flow, State, and Persistence
The CRDs are declarative cluster API definitions. Once applied, Kubernetes persists snapshot resources and allows controllers to update status subresources while users create or delete snapshot intent objects. The v4.5.0 file is byte-identical to the v4.4.0, v4.6.0, and v4.7.0 CRD files in this repository, so release changes come from controller image versions rather than schema changes.

## Dependencies and Integration Points
It depends on Kubernetes CRD support and integrates with `snapshot-controller:v6.3.1`, `csi-snapshotter:v6.3.1`, NFS storage classes, and any user-created `VolumeSnapshotClass` using `driver: nfs.csi.k8s.io`.

## Risks and Test Signals
Risks are cluster-wide API replacement, accidental removal of a served version still used by clients, and controller/schema version skew. Test signals are successful API discovery for `snapshot.storage.k8s.io/v1`, the snapshot controller staying ready after CRD install, successful creation of snapshot class/content/snapshot resources, and status updates through the status subresources.
