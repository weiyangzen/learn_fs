<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml -->
# sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml

Purpose: PVC restore example from a Longhorn VolumeSnapshot created from another PVC.

Important APIs/types/functions: PVC `test-restore-snapshot-pvc` uses `dataSource` referencing `VolumeSnapshot test-snapshot-pvc`.

Control flow: once the source snapshot is ready, CSI provisions a new Longhorn volume from that snapshot.

State and persistence: restored filesystem/block contents persist in the new PVC.

Dependencies/integration points: depends on CSI snapshot controller, Longhorn snapshotter, source snapshot readiness, and StorageClass `longhorn`.

Risks/test signals: restore size must be valid and source snapshot must not be deleted prematurely. Test signals are snapshot `readyToUse`, PVC Bound, and restored data checks.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml -->
