<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml

Purpose: VolumeSnapshotClass for Longhorn CSI snapshots.

Important APIs/types/functions: `VolumeSnapshotClass` named `longhorn`, driver `driver.longhorn.io`, `deletionPolicy: Delete`, with commented CSI snapshotter secret parameters.

Control flow: VolumeSnapshot objects referencing this class route snapshot operations to the Longhorn CSI driver.

State and persistence: class controls snapshot lifecycle behavior but stores no data.

Dependencies/integration points: depends on external snapshotter CRDs/controller and Longhorn CSI snapshot support.

Risks/test signals: Delete policy removes snapshots when snapshot objects are deleted; secret parameters may be required for secured setups. Test signals are snapshot creation/deletion and restore from snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml -->
