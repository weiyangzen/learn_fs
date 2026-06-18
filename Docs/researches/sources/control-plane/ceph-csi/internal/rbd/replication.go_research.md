<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/replication.go -->
# sources/control-plane/ceph-csi/internal/rbd/replication.go

## Purpose
`replication.go` contains small RBD-specific helpers for mirrored/replicated volumes: repairing image IDs after resync and safely disabling mirroring depending on local primary/secondary state.

## Important APIs, Types, And Functions
`rbdVolume.RepairResyncedImageID` updates the OMAP image ID after a mirror resync replaces the local image. `DisableVolumeReplication` operates on the `types.Mirror` interface and validates primary/secondary behavior against go-ceph mirroring states.

## Control Flow
`RepairResyncedImageID` returns immediately unless the resync is ready, connects to the volume journal, then calls `repairImageID` with `force=true`. `DisableVolumeReplication` allows a secondary image to succeed only when global status reports local site `up` and `replaying`; otherwise it returns invalid-argument style errors. For primary images it disables mirroring, then verifies the image reports disabled state.

## State And Persistence
Persistent state is Ceph-CSI volume journal OMAP image ID and Ceph RBD mirror state. Runtime state is the mirror status returned by the `types.Mirror` implementation.

## Dependencies And Integration Points
It depends on go-ceph RBD mirror status constants, internal RBD errors, the volume journal, and the replication/mirroring interfaces under `internal/rbd/types`. It is used by replication controller/server flows outside this subset.

## Risks
After disabling mirroring, state may remain transitional; the function treats non-disabled state as aborted. Secondary cleanup success is deliberately narrow and depends on global status semantics. Repairing image IDs assumes the resynced image is accessible and journal credentials are valid.

## Test Signals
No direct tests in this subset. Mirror status tests should cover primary disable success, disabled-state lag, healthy secondary replaying success, unhealthy secondary failures, and image ID repair only when ready.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/replication.go -->
