<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml

Purpose: creates a point-in-time snapshot of the example CephFS PVC.
Important APIs/types/functions: `VolumeSnapshot`, `volumeSnapshotClassName: csi-cephfsplugin-snapclass`, and `source.persistentVolumeClaimName: cephfs-pvc`.
Control flow: the snapshot controller creates a `VolumeSnapshotContent`, calls the CephFS CSI snapshotter, and records readiness in `VolumeSnapshot.status`. Snapshot state is stored both in Kubernetes snapshot objects and backend CephFS snapshot/subvolume metadata. Dependencies are `snapshotclass.yaml`, snapshot CRDs/controller, a bound source PVC, and CephFS CSI snapshot support. Risks: snapshots are crash-consistent at the volume level, deletion policy is defined by the class, and source PVC writes may continue during snapshot creation. Test signals: `readyToUse: true`, non-empty restore size, and `pvc-restore.yaml` can create a usable volume from it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml -->
