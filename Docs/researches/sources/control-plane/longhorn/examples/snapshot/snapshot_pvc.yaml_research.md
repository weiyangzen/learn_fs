<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml

Purpose: VolumeSnapshot example that snapshots an existing PVC.

Important APIs/types/functions: `VolumeSnapshot` `test-snapshot-pvc`, class `longhorn`, source `persistentVolumeClaimName: test-vol`.

Control flow: snapshot controller calls Longhorn CSI snapshotter to create a point-in-time snapshot of the named PVC.

State and persistence: snapshot metadata persists in Kubernetes and Longhorn; data is retained according to snapshot class deletion policy and Longhorn behavior.

Dependencies/integration points: depends on source PVC `test-vol`, CSI snapshot controller, VolumeSnapshotClass `longhorn`, and Longhorn snapshot APIs.

Risks/test signals: source PVC must exist and be in a suitable state. Test signals are VolumeSnapshot ready status, VolumeSnapshotContent creation, and restore test.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml -->
