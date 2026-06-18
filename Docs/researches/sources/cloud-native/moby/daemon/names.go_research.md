# sources/cloud-native/moby/daemon/names.go

## Purpose
This file manages container name generation, validation, reservation, conflict handling, and release.

## Important APIs, Types, And Functions
Methods include `registerName`, `generateIDAndName`, `reserveName`, `releaseName`, and `generateAndReserveName`. It uses `containersReplica.ReserveName`, `ReleaseName`, `Snapshot().GetID`, `stringid.GenerateRandomID`, `stringid.TruncateID`, and `namesgenerator.GetRandomName`.

## Control Flow
`registerName` rejects empty IDs and already-loaded containers, generates a name if missing, or reserves the persisted name. `generateIDAndName` creates an ID and either generates/reserves a random name or reserves the requested name. `reserveName` validates name characters after trimming a leading slash, ensures a leading slash, reserves it, and converts conflicts into `nameConflictError` with the existing container ID. `generateAndReserveName` tries six generated names before falling back to the truncated container ID.

## State, Persistence, And Dependencies
Name state is maintained in the daemon's `containersReplica` reservation index and later persisted by container metadata. There is no direct disk write here. Dependencies include containerd conflict detection, name regex from `daemon/names`, random Docker name generator, and errdefs invalid parameter errors.

## Integration Points
This file is used by container create and restore paths to preserve globally unique container names across daemon state.

## Risks And Edge Cases
Name validation allows a single-character alphanumeric name and subsequent alphanumeric/underscore/dot/hyphen characters. Conflict handling does an extra lookup that can itself fail. Fallback to truncated ID can still conflict if replica state is corrupt.

## Test Signals
No direct tests in this item. Behavior is historically covered by container create/name conflict integration tests.
