## sources/control-plane/ceph-csi/internal/cephfs/store/fsjournal.go

Purpose: Implements CephFS volume and snapshot journal operations that provide idempotent CSI name-to-backend-object mapping.

Important types/functions: Global `VolJournal`, `SnapJournal`, `VolumeGroupJournal`; `VolumeIdentifier`; `SnapshotIdentifier`; `CheckVolExists`; `UndoVolReservation`; `updateTopologyConstraints`; `getEncryptionConfig`; `ReserveVol`; `ReserveSnap`; `UndoSnapReservation`; `CheckSnapExists`; and `SetSubVolCSIMetadata`.

Control flow: `CheckVolExists` connects to the volume journal, checks request-name reservation, validates existing backend subvolume or clone state, handles clone pending/in-progress/failed cleanup, retrieves root path, cleans stale reservations, and generates CSI volume ID. `ReserveVol` applies topology constraints, reserves a UUID/name in OMAP, sets `volOptions.VolID`, and generates CSI volume ID. Snapshot functions mirror this for snapshot reservations and existing snapshot validation. `SetSubVolCSIMetadata` decomposes a CSI ID, resolves monitors/subvolume group, connects, and writes Kubernetes PV/PVC metadata to the subvolume.

State and persistence: Uses RADOS OMAP journal objects in the CephFS metadata pool and namespace to persist CSI request names, UUIDs, image/subvolume names, parent relationships, encryption IDs, owners, and backing snapshot IDs. It also reads/writes CephFS subvolumes/snapshots and metadata via core clients.

Dependencies and integrations: Depends on internal journal package, core volume/snapshot APIs, util CSI ID generation/decomposition, topology selection, KMS encryption type, Kubernetes metadata preparation, and Ceph cluster connections.

Risks and tests: Correct locking by controller request name is required; comments explicitly warn that journal operations must be called under locks. Rollback paths are complex, especially clone failure cleanup and stale OMAP removal. `CheckVolExists` cleans intermediate clone snapshots when appropriate. Test coverage in this subset is absent; integration should cover stale reservation repair, clone retry progress, topology pool selection, encrypted volumes, and snapshot reservation cleanup.
