<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml

Purpose: creates a CSI snapshot of the baseline RBD PVC.
Important APIs/types/functions: `VolumeSnapshot`, `volumeSnapshotClassName: csi-rbdplugin-snapclass`, and source PVC `rbd-pvc`.
Control flow: the snapshot controller asks RBD CSI to snapshot the backing image and records readiness/restore size in Kubernetes snapshot status. State is persisted in `VolumeSnapshot`, `VolumeSnapshotContent`, and RBD snapshot metadata. Dependencies are snapshot CRDs/controller, RBD snapshot class, and a bound source PVC. Risks: active filesystem writes may require application quiescing for application consistency, delete policy removes backend snapshot data, and image features must support snapshot/clone use. Test signals: snapshot `readyToUse` true, RBD lists a snapshot, and `pvc-restore.yaml` succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml -->
