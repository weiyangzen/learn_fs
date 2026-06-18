# sources/control-plane/ceph-csi/internal/rbd/group_controllerserver.go

## Purpose
Implements CSI group-controller RPCs for RBD volume group snapshots: create, delete, and get. It orchestrates volume resolution, temporary or existing librbd group usage, consistent group snapshot creation, cleanup, and CSI response conversion.

## Important APIs, Types, And Functions
`CreateVolumeGroupSnapshot` handles request validation, locking, manager setup, volume resolution, group matching, optional existing group reuse, temporary group creation, volume preparation, group snapshot lookup/create, and response assembly. `DeleteVolumeGroupSnapshot` resolves and deletes a group snapshot by ID. `GetVolumeGroupSnapshot` resolves and returns a group snapshot by ID.

## Control Flow
Create validates group-controller capability and locks by requested group snapshot name. It resolves all source volume IDs via `NewManager`, ensures volumes are all in the same group or no group, reuses an existing group if the first volume already belongs to one, returns an existing group snapshot if found by name, prepares each volume for snapshot, creates a temporary group when needed, adds volumes if the group is empty, asks the manager to create the group snapshot, converts to CSI, and uses defers to remove volumes/delete temporary groups on failure or after use. Delete/get validate capability, lock by group snapshot ID, resolve through the manager, translate not-found into CSI success for delete or NotFound for get, and call delete or conversion.

## State And Persistence
Persistent state is handled through manager/group code: RBD groups, group snapshots, per-volume snapshot images, journal reservations, and volume maps. In-memory `VolumeGroupLocks` prevent concurrent operations on the same group snapshot name/ID. Temporary groups are normally deleted after the operation to avoid images being stuck in a single group.

## Dependencies And Integration Points
Depends on CSI group-controller protobufs, manager abstractions, RBD group errors, common CSI capability validation, util locks, credentials, and logging. Feature availability is gated earlier by driver/identity librbd symbol detection.

## Risks And Test Signals
Risks include cleanup failures leaving images in temporary groups, incomplete idempotency checks for existing group snapshots, all-or-nothing preparation across multiple volumes, and FIXME gaps around delete request validation. There are no direct unit tests for this file; it needs integration coverage with librbd group snapshot support.
