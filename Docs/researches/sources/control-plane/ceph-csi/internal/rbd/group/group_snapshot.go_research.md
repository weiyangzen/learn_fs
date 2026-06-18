# sources/control-plane/ceph-csi/internal/rbd/group/group_snapshot.go

## Purpose
Implements the `types.VolumeGroupSnapshot` abstraction backed by RBD group snapshots and RADOS volume-group journal mappings.

## Important APIs, Types, And Functions
`volumeGroupSnapshot` embeds `commonVolumeGroup` and tracks snapshot objects plus snapshots it owns for cleanup. `GetVolumeGroupSnapshot` resolves an existing group snapshot from a CSI ID and journal volume map. `NewVolumeGroupSnapshot` records newly created snapshot IDs/names in the journal and stores the group ID on each snapshot. Methods `ToCSI`, `Destroy`, `Delete`, and `ListSnapshots` expose CSI conversion, cleanup, deletion, and enumeration.

## Control Flow
Lookup initializes common group state, fetches journal attributes, resolves each snapshot ID through the provided resolver, and stores resolved snapshots for later destruction. Creation initializes common state, validates existing attributes, builds a snapshot ID-to-name map, updates each snapshot with its group ID, and writes the mapping through `AddVolumesMapping`. Delete iterates all child snapshots and deletes them before removing the common journal reservation.

## State And Persistence
Persistent state includes journal attributes and volume maps, snapshot image metadata linking snapshots to the group ID, and backend snapshot images themselves. In-memory `snapshotsToFree` prevents leaks for resolved snapshot handles.

## Dependencies And Integration Points
Depends on CSI group snapshot protobufs, common group journal utilities, `types.SnapshotResolver`, `types.Snapshot`, and RBD error sentinels. It is created and resolved by `manager.go` and returned by `group_controllerserver.go`.

## Risks And Test Signals
Risks include partial creation where some snapshots have group metadata but journal mapping fails, delete stopping on the first failed child snapshot, and map iteration order producing non-deterministic CSI snapshot ordering. No direct tests exist in this subset.
