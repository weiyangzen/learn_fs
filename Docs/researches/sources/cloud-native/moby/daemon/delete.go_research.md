# sources/cloud-native/moby/daemon/delete.go

## Purpose
Implements container removal and cleanup, including force handling, link removal, stats stop, graceful stop, RW layer release, filesystem removal, mount/volume cleanup, name release, metrics, and destroy event emission.

## Important APIs, Types, And Functions
- `ContainerRm` is the public entrypoint.
- `containerRm` resolves the container, serializes deletion with `RemovalInProgress`, handles link-only removal, and records delete metrics.
- `rmLink` removes a legacy link name from the parent container and updates networking.
- `cleanupContainer` performs running-container checks, stop/kill, dead-state checkpoint, layer release, root deletion, link index deletion, SELinux release, store removal, mount-point removal, state/metrics cleanup, and destroy event logging.

## Control Flow
Removal first marks `RemovalInProgress` atomically to avoid duplicate deletes. Non-force removal rejects running, paused, or restarting containers with conflict errors. Force removal kills running containers if necessary, stops stats, attempts a short graceful stop, marks the container dead and checkpoints it, releases the RW layer, removes the container root under lock, deletes link/name/store state, removes volumes if requested, and marks the state removed.

## State And Persistence
Mutates container state flags, checkpoint files, layer store references, container root directory, link index, name reservations, SELinux label reservations, in-memory and view DB stores, mount points/volumes, metrics, and event history.

## Dependencies And Integration Points
Depends on container state, daemon kill/stop paths, stats collector, image service layer release, `containerfs.EnsureRemoveAll`, SELinux, mount-point removal, network link update, metrics, and event logging.

## Risks And Edge Cases
The removal lock prevents duplicate deletes but returns conflict while removal is active. If layer release fails, the RW layer reference is restored and the removal error is stored. Windows filesystem deletion requires holding the container lock to avoid open-file races. Link-only removal rejects default link names.

## Test Signals
`delete_test.go` verifies useful conflict messages for paused/restarting/running containers and duplicate removal detection.
