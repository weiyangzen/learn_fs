# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/snapshotclass.yaml

Purpose: defines the example `VolumeSnapshotClass` used for NFS CSI snapshot creation.

Important APIs/types/functions: the object is `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-nfs-snapclass`, with driver `nfs.csi.k8s.io` and `deletionPolicy: Delete`.

Control flow: a `VolumeSnapshot` that references this class is reconciled by the snapshot controller, then by the NFS controller's `csi-snapshotter` sidecar, which calls the NFS CSI driver snapshot RPCs.

State and persistence: the class is persistent cluster configuration. Snapshot instances and contents persist separately; `Delete` instructs cleanup of snapshot content when the snapshot object is removed.

Dependencies and integration points: requires snapshot CRDs, snapshot-controller RBAC/deployment, and a controller deployment containing `csi-snapshotter`. It must use the same driver name as the `CSIDriver` and NFS plugin.

Risks: `Delete` is convenient for examples but can remove backend snapshot data. If the class exists without matching sidecars or CRDs, snapshot objects remain pending.

Test signals: apply with server-side dry run, create `snapshot-nfs-dynamic.yaml`, observe `VolumeSnapshotContent`, delete the snapshot, and verify content cleanup follows the policy.
