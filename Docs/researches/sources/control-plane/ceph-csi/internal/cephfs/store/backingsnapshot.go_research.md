## sources/control-plane/ceph-csi/internal/cephfs/store/backingsnapshot.go

Purpose: Manages RADOS reftracker state for snapshot-backed CephFS volumes so backing snapshots are retained while referenced and removed when safe.

Important functions: `fmtBackingSnapshotReftrackerName`, `AddSnapshotBackedVolumeRef`, `UnrefSnapshotBackedVolume`, and `UnrefSelfInSnapshotBackedVolumes`.

Control flow: Add opens an ioctx in the metadata pool/namespace, adds refs for the backing snapshot ID and new volume ID, registers cleanup to remove them on failure, then re-fetches the backing snapshot to detect delete races. Unref for a volume removes the volume ref and returns whether the reftracker object is deleted. Unref self masks/removes the snapshot's own ref during snapshot deletion and returns whether no dependent snapshot-backed volumes remain.

State and persistence: Persists reftracker objects named `rt-backingsnapshot-<snapshotID>` in RADOS. Uses normal and mask ref types to distinguish dependent volumes from the snapshot self reference.

Dependencies and risks: Depends on RADOS ioctx, reftracker wrappers, store snapshot lookup, and cluster credentials. Races are partially handled with revalidation and `ErrObjectOutOfDate` handling in callers. Cleanup logging warns about orphaned reftracker objects if removal fails. Integration tests should simulate concurrent snapshot delete and volume create/delete.
