<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot.go -->
# sources/control-plane/ceph-csi/internal/rbd/snapshot.go

## Purpose
`snapshot.go` implements RBD snapshot image creation, conversion between RBD volume and snapshot models, CSI snapshot rendering, snapshot deletion, snapshot image creation by parent snapshot ID, group snapshot association, and snapshot ID lookup for diff iteration.

## Important APIs, Types, And Functions
Important functions include `createRBDClone`, `cleanUpSnapshot`, `rbdVolume.toSnapshot`, `rbdSnapshot.toVolume`, `rbdSnapshot.ToCSI`, `rbdSnapshot.Delete`, `undoSnapshotCloning`, `rbdVolume.NewSnapshotByID`, `rbdSnapshot.SetVolumeGroup`, `rbdSnapshot.GetSize`, `rbdSnapFromSnapshot`, and `rbdSnapshot.getRBDSnapID`.

## Control Flow
`createRBDClone` creates a parent snapshot, clones it, and optionally deletes the temporary snapshot. `cleanUpSnapshot` removes both the RBD snapshot and backing image, ignoring not-found cases. `ToCSI` validates IDs, obtains creation time, and emits a ready CSI snapshot. `Delete` converts the snapshot to a volume, connects, removes snapshot image and snapshot, then undoes the journal reservation. `NewSnapshotByID` reserves a journal entry, forces layering and deep-flatten features, clones by source snapshot ID into a new image, creates a snapshot on that image, repairs the image ID in the journal, and uses defers to remove the snapshot image on failure.

## State And Persistence
Persistent state includes RBD snapshots, cloned snapshot backing images, journal reservations, journal image IDs, optional group IDs, and CSI-visible snapshot metadata. Runtime state includes copied encryption helpers and open IO contexts/images. Conversion helpers intentionally copy encryption pointers rather than using clone-copy helpers because volume and snapshot can share the same ID.

## Dependencies And Integration Points
It depends on go-ceph RBD clone/snapshot APIs, CSI snapshot protobufs, journal helpers in `rbd_journal.go`, shared image helpers in `rbd_util.go`, internal snapshot interfaces, and group snapshot support.

## Risks
Comments note a known modeling issue: snapshot resolution can set `RbdImageName` to the parent/source name, which can make deletion dangerous if not fixed by manager code. Defers in `NewSnapshotByID` remove images after failure and must not run after success. `createRBDClone` returns nil when clone fails and `deleteSnap` is false only after wrapping `err`, so callers must inspect behavior carefully. Snapshot deletion should run under request-name locks because it manipulates OMAP.

## Test Signals
Only `snapshot_test.go` outside this requested output directly covers `ToCSI` and `rbdSnapFromSnapshot`; this subset has no mapped snapshot test file. Backend clone/delete behavior needs integration testing with Ceph.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot.go -->
