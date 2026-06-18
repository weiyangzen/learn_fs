<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml -->
# sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml

Purpose: VolumeSnapshotContent example that imports an existing Longhorn backup as a CSI snapshot content object.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent`, driver `driver.longhorn.io`, class `longhorn`, `deletionPolicy: Delete`, `source.snapshotHandle: bs://...`, and `volumeSnapshotRef`.

Control flow: snapshot controller binds this content to the referenced VolumeSnapshot, allowing restore PVCs to use the backup-backed snapshot.

State and persistence: references external backupstore data through the snapshot handle; Kubernetes stores snapshot binding state.

Dependencies/integration points: depends on CSI snapshot CRDs/controller, Longhorn snapshotter, and a valid backupstore URL.

Risks/test signals: placeholder backup handle must be changed; Delete policy may remove snapshot content metadata or backend data depending on driver behavior. Test signals are bound VolumeSnapshotContent, snapshot ready status, and restore PVC success.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml -->
