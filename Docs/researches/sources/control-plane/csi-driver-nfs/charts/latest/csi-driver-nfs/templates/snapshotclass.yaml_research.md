# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: Optional `VolumeSnapshotClass` template for NFS CSI snapshots.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; Helm values `.Values.volumeSnapshotClass.create`, `.Values.volumeSnapshotClass.name`, `.Values.volumeSnapshotClass.annotations`, `.Values.volumeSnapshotClass.deletionPolicy`, `.Values.driver.name`, and `include "nfs.labels"`.

Control flow: Renders only when `volumeSnapshotClass.create` is true. It writes metadata labels, optional annotations, the CSI driver name, and deletion policy.

State and persistence: Persists cluster-scoped snapshot class configuration used by VolumeSnapshot admission/controller logic. It does not hold snapshot data.

Dependencies and integration points: Requires snapshot CRDs and a controller-side CSI snapshotter. The `driver` must match the `CSIDriver` and CSI plugin name.

Risks: Incorrect default-class annotations or deletion policy can affect all matching snapshots. The template assumes snapshot APIs already exist or are installed by this chart. Test signals: render with and without annotations, then validate with `kubectl apply --dry-run=server`.
