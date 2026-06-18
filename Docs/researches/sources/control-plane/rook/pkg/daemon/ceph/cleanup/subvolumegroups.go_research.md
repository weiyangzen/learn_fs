<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go

Purpose: cleans CephFS subvolumes inside a subvolume group before `CephFilesystemSubVolumeGroup` deletion, including CSI OMAP entries, pending clone cancellation, snapshot deletion, and subvolume removal.

Important APIs/types/functions: `SubVolumeGroupCleanup`, `CancelPendingClones`, `DeleteSubVolumeSnapshots`, `CleanUpOMAPDetails`, and `getOMAPValue`.

Control flow: `SubVolumeGroupCleanup` lists subvolumes for the filesystem/group. For each subvolume it derives and deletes CSI OMAP state, lists snapshots, cancels pending clones for those snapshots, deletes snapshots, and finally deletes the subvolume. It logs each failure and returns a wrapped aggregate last error if cleanup did not fully succeed.

State and persistence behavior: local state is only temporary lists and `retErr`; persistent effects occur in CephFS and RADOS OMAP objects through Ceph client commands. `getOMAPValue` derives `csi.volume.<uuid>` from CSI-style subvolume names.

Dependencies and integration points: depends on `clusterd.Context`, Ceph client helpers for CephFS subvolume/snapshot/clone commands and OMAP operations, CSI naming conventions, and cleanup logging.

Risks: non-CSI subvolume names fail OMAP derivation and mark cleanup failed. Returning only the latest error can hide earlier failures. Pending clone cancellation aborts on the first clone error for a snapshot set. OMAP deletion before snapshot/subvolume removal may leave inconsistent CSI metadata on later failures.

Test signals: empty group, CSI-named subvolume cleanup, OMAP value/key deletion, pending clone cancellation, snapshot deletion, subvolume deletion, invalid subvolume names, and partial error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go -->
