<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml

Purpose: VolumeSnapshot object that binds to pre-created VolumeSnapshotContent for an existing backup.

Important APIs/types/functions: `VolumeSnapshot` `test-snapshot-existing-backup`, class `longhorn`, source `volumeSnapshotContentName: test-existing-backup`.

Control flow: snapshot controller binds the snapshot to named content rather than creating a new snapshot from a PVC.

State and persistence: stores Kubernetes snapshot object state; actual data remains in the referenced backupstore.

Dependencies/integration points: depends on `existing_backup.yaml` content and CSI snapshot CRDs/controller.

Risks/test signals: names and namespace must match the content's `volumeSnapshotRef`. Test signals are bound snapshot, ready status, and restore PVC success.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml -->
