<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml

Purpose: restores an NFS CSI PVC from a snapshot.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, source `nfs-pvc-snapshot`, and StorageClass `rook-nfs`.
Control flow: the provisioner resolves the ready snapshot and asks the NFS CSI driver to create a new 1Gi volume/export from it. State is a new PVC/PV and backend exported volume; the snapshot object remains separate. Dependencies are `snapshot.yaml`, `snapshotclass.yaml`, snapshot CRDs/controller, and NFS CSI restore support. Risks: snapshot may not be ready, restore size must be compatible, and deletion policies can remove backend snapshot content. Test signals: restored PVC Bound, pod mount succeeds, and data reflects the snapshot point.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml -->
