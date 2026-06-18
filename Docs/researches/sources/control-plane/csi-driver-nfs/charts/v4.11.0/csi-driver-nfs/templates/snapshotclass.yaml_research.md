# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: 4.11.0 optional VolumeSnapshotClass.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; values for create flag, name, deletionPolicy, and driver name.

Control flow: Renders only when `volumeSnapshotClass.create` is true and emits name, driver, and deletionPolicy.

State and persistence: Cluster-scoped snapshot class policy.

Dependencies and integration points: Snapshot CRDs, snapshot-controller, CSI snapshotter, and matching driver name.

Risks: No labels/annotations in this version; deletion policy mistakes affect backend snapshot retention. Test signals: dry-run and VolumeSnapshot create/delete with the class.
