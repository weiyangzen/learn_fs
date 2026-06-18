<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go

## Purpose
`rbd_journal.go` coordinates Ceph-CSI journal/OMAP reservations for RBD volumes and snapshots. It validates in-memory objects, detects existing reservations, repairs stale or incomplete transactions, generates CSI IDs, updates topology and image IDs, and regenerates journal state for static or migrated volumes.

## Important APIs, Types, And Functions
Validation helpers are `validateNonEmptyField`, `validateRbdSnap`, and `validateRbdVol`. Core operations are `checkSnapCloneExists`, `rbdVolume.Exists`, `repairImageID`, `reserveSnap`, `reserveVol`, `undoSnapReservation`, `undoVolReservation`, `updateTopologyConstraints`, `RegenerateJournal`, and `rbdVolume.storeImageID`. `getEncryptionConfig` maps configured block/file encryption to journal fields.

## Control Flow
Reservation lookup uses `volJournal` or `snapJournal` to connect to RADOS OMAPs. Existing snapshot reservations are rolled back if backing images are missing, or rolled forward by recreating missing snapshots and storing image IDs. Existing volume reservations are checked against topology, image existence, parent-clone recovery, size compatibility, and encryption configuration before returning generated CSI IDs. New reservations allocate names and UUIDs with pool IDs, then generate CSI volume/snapshot handles. `RegenerateJournal` decomposes an existing volume handle, maps cluster IDs, reserves or repairs OMAP state, updates owner and metadata, and returns a regenerated volume handle.

## State And Persistence
Persistent state is Ceph-CSI journal OMAP data: request-name-to-image reservations, image attributes, image IDs, group IDs, owner fields, and pool IDs. The code also writes RBD image metadata during regeneration. Defer blocks restore in-memory reservation fields on error and undo OMAP reservations for failed creates.

## Dependencies And Integration Points
This file depends on `internal/journal`, RADOS pool ID helpers, Kubernetes metadata preparation, encryption configuration, topology matching, and snapshot/volume helpers from `rbd_util.go` and `snapshot.go`. It is a central integration point for controller create/delete volume and snapshot flows.

## Risks
The comments correctly warn that reservation checks must run under request-name locks; otherwise OMAP garbage collection and roll-forward/rollback can race. Journal pool ID conversion failures can leak images, as TODOs note. Recovery paths manipulate real images and snapshots when stale OMAP is detected. `RegenerateJournal` is complex and updates both OMAP and image metadata; partial failure handling depends on defer-based undo after reservation.

## Test Signals
No direct tests are included in this subset. Existing behavior is indirectly exercised by controller integration/e2e tests. High-value tests would mock journal connections for stale reservation cleanup, image ID repair, topology mismatch, owner reset, and journal regeneration idempotence.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go -->
