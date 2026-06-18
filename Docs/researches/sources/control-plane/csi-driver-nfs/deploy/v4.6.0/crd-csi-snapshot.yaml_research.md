# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/crd-csi-snapshot.yaml

## Purpose
This v4.6.0 file installs the CSI snapshot CRDs used by the NFS CSI bundle. It is byte-identical to the v4.4.0, v4.5.0, and v4.7.0 snapshot CRD manifests in this repository.

## Important APIs, Types, and Functions
It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io`, each with `v1` and `v1beta1` served versions. The schemas capture snapshot sources, class references, CSI driver names, deletion policy, snapshot handles, volume handles, volume snapshot references, restore size, ready state, errors, and status subresources.

## Control Flow, State, and Persistence
Applying the file adds persistent cluster API types. Users and controllers then create and mutate custom resources; the snapshot controller and CSI snapshotter update status and content bindings as the snapshot lifecycle advances.

## Dependencies and Integration Points
It integrates with `snapshot-controller:v6.3.3`, `csi-snapshotter:v6.3.3`, RBAC for both snapshot and NFS controllers, and storage classes/snapshot classes for `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks include CRD replacement blast radius, compatibility with stored `v1beta1` clients, and controller readiness failures if CRDs are absent. Test signals include served API discovery, successful status-subresource writes, snapshot controller readiness, `VolumeSnapshotContent` binding, and PVC restore flows using `restoreSize`.
