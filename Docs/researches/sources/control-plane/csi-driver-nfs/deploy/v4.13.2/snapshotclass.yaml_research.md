## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/snapshotclass.yaml

Purpose: Provides a default example `VolumeSnapshotClass` for the NFS CSI driver. It connects snapshot requests to driver `nfs.csi.k8s.io` and chooses `deletionPolicy: Delete`, meaning the backing snapshot should be removed when the snapshot content is deleted.

Important APIs and types: The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-nfs-snapclass`. The two behavioral fields are `driver: nfs.csi.k8s.io` and `deletionPolicy: Delete`; no driver-specific parameters or default-class annotations are set.

Control flow: A `VolumeSnapshot` can reference this class by `.spec.volumeSnapshotClassName`. The snapshot controller uses it when binding a `VolumeSnapshotContent`, and the CSI snapshotter sidecar routes snapshot calls to the NFS CSI driver based on the matching driver name. Because there is no default annotation, snapshots that omit `volumeSnapshotClassName` need another default class or explicit class selection.

State and persistence behavior: This is cluster-scoped policy stored in the Kubernetes API. It does not create snapshots by itself. Its deletion policy is copied into dynamically provisioned snapshot content, so changing or deleting the class after creation does not necessarily change already-created content behavior.

Dependencies and integration points: Depends on the snapshot CRDs from `crd-csi-snapshot.yaml`, the snapshot controller deployment/RBAC, and the NFS controller sidecar `csi-snapshotter`. It must match the `CSIDriver` and CSI plugin name `nfs.csi.k8s.io`.

Risks: `deletionPolicy: Delete` is destructive for the external snapshot lifecycle. Operators expecting retained snapshots should change this to `Retain` before production use. Since this is only an example class and lacks parameters, environment-specific snapshot behavior must come from the driver defaults. Missing CRDs cause apply failure.

Test signals: Apply after the CRDs and verify `kubectl get volumesnapshotclass csi-nfs-snapclass`. Create a PVC-backed `VolumeSnapshot` that references the class, confirm `VolumeSnapshotContent.spec.deletionPolicy` becomes `Delete`, and validate snapshot deletion removes the content and triggers driver-side cleanup.
