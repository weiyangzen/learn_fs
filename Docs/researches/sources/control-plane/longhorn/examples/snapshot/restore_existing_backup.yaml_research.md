<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml -->
# sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml

Purpose: PVC restore example using a VolumeSnapshot that represents an existing Longhorn backup.

Important APIs/types/functions: PVC `test-restore-existing-backup` uses `dataSource` pointing to `VolumeSnapshot test-snapshot-existing-backup`, StorageClass `longhorn`, RWO, and 2Gi request.

Control flow: CSI provisioner creates a new Longhorn volume from the snapshot/backup data source.

State and persistence: restored data persists in the new PVC/Longhorn volume.

Dependencies/integration points: depends on snapshot content and snapshot object being ready, Longhorn backupstore access, and CSI data source support.

Risks/test signals: requested size must be sufficient for restore; missing backupstore credentials break provisioning. Test signals are PVC Bound, Longhorn restore progress, and data validation in a consumer pod.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml -->
