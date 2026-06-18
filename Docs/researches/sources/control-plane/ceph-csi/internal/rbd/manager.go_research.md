# sources/control-plane/ceph-csi/internal/rbd/manager.go

## Purpose
Provides a high-level manager that connects CSI request parameters/secrets to RBD volumes, snapshots, volume groups, and volume group snapshots. It is the bridge between controller RPCs and lower-level RBD group/journal abstractions.

## Important APIs, Types, And Functions
`rbdManager` stores driver instance, parameters, secrets, cached credentials, and cached volume-group journal. It implements `types.Manager` through `NewManager`, `Destroy`, `GetVolumeByID`, `GetSnapshotByID`, `GetVolumeGroupByID`, `MakeVolumeGroupID`, `CreateVolumeGroup`, `GetVolumeGroupSnapshotByID`, `GetVolumeGroupSnapshotByName`, `CreateVolumeGroupSnapshot`, `RegenerateVolumeGroupJournal`, `CompareVolumesInGroup`, and `VolumesInSameGroup`. Helpers include `getCredentials`, `getVolumeGroupNamePrefix`, `getVolumeGroupJournal`, and `getGroupUUID`.

## Control Flow
Volume and snapshot lookup lazily create credentials and call existing RBD ID resolvers, wrapping common missing image/pool errors. Group creation validates cluster/pool parameters, connects the volume-group journal, checks or reserves a name/UUID, gets monitor and pool IDs, generates a CSI handle, resolves a group object, and creates the backend group. Group snapshot lookup by name reserves or reuses a group UUID, builds a CSI ID, resolves a group snapshot, and verifies it has snapshots. Snapshot creation reserves a UUID, generates a group ID, returns an existing complete snapshot if present, otherwise calls `vg.CreateSnapshots`, registers the new group snapshot in the journal, and cleans up child snapshots on failure. Regeneration rebuilds journal mappings after failover/migration using mapped cluster information and volume IDs.

## State And Persistence
Persistent state is the RADOS volume-group journal: reservations, generated UUIDs, group names, and volume maps. It also creates librbd groups/snapshots via lower layers. Runtime state includes cached credentials and journal handles cleaned by `Destroy`.

## Dependencies And Integration Points
Depends on journal APIs, util CSI ID/cluster/pool mapping helpers, RBD volume/snapshot resolvers, `internal/rbd/group`, and `types` interfaces. It is used by `group_controllerserver.go` and CSI-Addons RBD volume-group/replication services.

## Risks And Test Signals
Risks include inconsistent use of pool vs journalPool during undo paths, incomplete existing snapshot validation by length only, cached `mgr.creds` assumptions before some methods use it, partial journal regeneration on errors, and cleanup closure behavior when reservations are reused. `manager_test.go` covers only `MakeVolumeGroupID` formatting/error paths.
