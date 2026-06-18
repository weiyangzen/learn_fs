<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml

Purpose: restores a new CephFS PVC from a `VolumeSnapshot`.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, snapshot `cephfs-pvc-snapshot`, and StorageClass `rook-cephfs`.
Control flow: the external provisioner resolves the snapshot object, invokes CSI create-from-snapshot on the CephFS driver, and binds a new PVC with restored content. State lives in the new PVC/PV and backend CephFS subvolume; source snapshot state remains separate. Dependencies are snapshot CRDs/controller, a ready snapshot from `snapshot.yaml`, and matching CSI snapshot class. Risks: restore fails if snapshot is not ready, class or source volume size is incompatible, or snapshot deletion policy removed backend data. Test signals: restored PVC Bound, data matches snapshot point in time, and the PVC can mount through `pod.yaml`-style workload.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml -->
