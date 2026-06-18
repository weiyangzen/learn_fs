# sources/control-plane/csi-driver-host-path/pkg/hostpath/groupcontrollerserver.go

## Purpose
This file implements the CSI group controller service for volume group snapshot create, delete, get, and capability reporting. It creates one ordinary snapshot per source volume and links them through a persisted group snapshot record.

## Important APIs, Types, And Functions
RPCs are `GroupControllerGetCapabilities`, `CreateVolumeGroupSnapshot`, `DeleteVolumeGroupSnapshot`, and `GetVolumeGroupSnapshot`. `validateGroupControllerServiceRequest` accepts only `CREATE_DELETE_GET_VOLUME_GROUP_SNAPSHOT`. It uses `state.GroupSnapshot`, `state.Snapshot`, uuid generation, protobuf timestamps, and `optionsFromParameters`/`createSnapshotFromVolume`.

## Control Flow
Create validates name and source volume IDs, locks state, and handles idempotency by group snapshot name and matching source volume IDs. For a new group, it allocates a group UUID, copies source IDs, loops over each source volume, validates snapshot parameters, creates a snapshot file, stores a snapshot record with `GroupSnapshotID`, and finally stores the group record. Delete finds the group, removes each snapshot file and state record, then deletes the group record. Get validates requested snapshot IDs against the group and returns each snapshot's metadata.

## State, Persistence, And Dependencies
Group state is persisted in `state.json` alongside individual snapshots. Snapshot files are stored in the same `.snap` path scheme as ordinary snapshots. There is no transactional rollback across multiple snapshot files/state writes.

## Integration Points
Group snapshot examples use the v1beta1 Kubernetes group snapshot API. The identity service advertises `GROUP_CONTROLLER_SERVICE`; the gRPC server always registers the group controller. The individual snapshot records also appear through normal snapshot listing with `GroupSnapshotId` set.

## Risks
The TODO notes missing cleanup on partial create failure; a failed later source can leave earlier snapshot files/state without a group record. `hp.state.UpdateSnapshot(snapshot)` errors are ignored inside the loop. Snapshot parameter handling uses the same tar options as ordinary snapshots. This test driver does not coordinate crash-consistent group snapshots; it snapshots volumes sequentially.

## Test Signals
Tests should cover capability response, create idempotency with same/different source sets, partial source missing behavior, delete idempotency for not found, get with mismatched snapshot IDs, parameter validation, and cleanup of all member snapshots.
