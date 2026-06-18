# sources/control-plane/ceph-csi/internal/journal/voljournal.go

## Purpose
`voljournal.go` implements Ceph-CSI volume and snapshot journal metadata. It preserves idempotency between orchestrator request names and generated Ceph object UUIDs, stores attributes in RADOS OMAPs, supports cleanup of stale reservations, and provides helper mappings for migration and mirroring.

## Important APIs, Types, And Functions
`Config` defines all OMAP object names and keys for volumes or snapshots. Constructors include `NewCSIVolumeJournal`, `NewCSISnapshotJournal`, and namespace-aware variants. `Connection` wraps a `util.ClusterConnection` and journal config. `ImageData` and `ImageAttributes` carry decoded reservation state. Main methods include `Connect`, `CheckReservation`, `UndoReservation`, `ReserveName`, `GetImageAttributes`, `StoreImageID`, `StoreAttribute`, `StoreGroupID`, `FetchAttribute`, `CheckNewUUIDMapping`, `ReserveNewUUIDMapping`, and `ResetVolumeOwner`.

## Control Flow And State
`CheckReservation()` looks up the request-name key in the CSI directory OMAP, decodes either legacy UUID-only or poolID/UUID values, resolves pool IDs to pool names, fetches per-object attributes, validates back-pointers, snapshot source, KMS ID, and encryption type, and cleans stale reservations when key data is missing. `ReserveName()` reserves a UUID OMAP first, writes the request-to-UUID mapping, then writes the per-UUID back-pointer and image metadata, with deferred cleanup on later failure. `UndoReservation()` deletes the UUID OMAP and then removes the request-name key.

## State And Persistence Behavior
Persistent state is split between a global CSI directory OMAP and per-UUID OMAP objects. Directory keys map CO names or old volume handles to UUIDs or encoded poolID/UUID values. Per-UUID OMAPs store request name, image name, image ID, group ID, snapshot source, encryption KMS, encryption type, owner, backing snapshot ID, and arbitrary prefixed attributes. The connection caches monitors, credentials, and the go-ceph cluster connection.

## Dependencies And Integration Points
The file depends on `go-ceph`, Google UUIDs, `util.CSIIdentifier`, pool lookup helpers, Ceph-CSI crypto types, and the OMAP helpers in `omap.go`. RBD, CephFS, NFS, and migration code use these methods to maintain idempotent volume and snapshot metadata.

## Risks And Edge Cases
The code expects callers to hold a request-name lock; without it, parallel create/delete operations can corrupt mappings. Crash windows exist between UUID object reservation, directory mapping, and per-UUID metadata writes, with later cleanup expected to recover. The non-legacy poolID decoding assumes a slash-separated value with expected components. `Destroy()` only clears metadata and does not call `conn.Destroy()`, so caller ownership of the cluster connection is important.

## Test Signals
No tests for this file are in the subset. High-value coverage would include legacy and poolID encoded mappings, stale cleanup paths, snapshot parent mismatch, KMS/encryption mismatch, UUID parse failures in undo, namespace behavior, arbitrary attribute store/fetch, and crash-window reconciliation.
