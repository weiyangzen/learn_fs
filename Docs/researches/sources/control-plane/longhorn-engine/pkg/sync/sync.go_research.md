## sources/control-plane/longhorn-engine/pkg/sync/sync.go

### Purpose
`sync.go` is the controller-side orchestration layer for Longhorn replica synchronization tasks. It coordinates snapshot delete/purge, replica add/rebuild, restore-replica attachment, snapshot clone, and snapshot hashing across the replicas known to an engine controller.

### Important APIs, Types, And Functions
`Task` wraps a `controller/client.ControllerClient`; `NewTask` binds the client lifetime to a context. `TaskError` aggregates per-replica failures as `ReplicaError` values. JSON-facing status structs mirror sync-agent responses for purge, rebuild, clone, and hash jobs.

Primary methods are `DeleteSnapshot`, `PurgeSnapshots`, `PurgeSnapshotStatus`, `AddRestoreReplica`, `AddReplica`, `VerifyRebuildReplica`, `StartWithReplicas`, `RebuildStatus`, `HashSnapshot`, `HashSnapshotStatus`, and `HashSnapshotCancel`. Package-level helpers include `CloneSnapshot`, `CloneStatus`, `GetSnapshotsInfo`, `getNonBackingDisks`, `checkIfVolumeHeadExists`, and the private operation guards `isRebuilding`, `isHashingSnapshot`, `isPurging`, `markSnapshotAsRemoved`, `checkAndResetFailedRebuild`, `checkAndExpandReplica`, `reloadAndVerify`, and `getTransferClients`.

### Control Flow
Snapshot deletion first refuses removal when any replica is rebuilding, then marks the snapshot removed on every RW replica and cancels any matching hash job. Purge snapshots lists all replicas, rejects rebuild or active purge conflicts, then fan-outs `SnapshotPurge` calls to each replica client and aggregates failures.

Adding a normal replica starts the volume if no replicas exist. Otherwise it expands or validates the new replica size, resets stale failed rebuild state if needed, creates the replica in WO mode, selects RW source replicas, marks the target as rebuilding, asks the controller for the rebuild file list, rejects any file list containing `volume-head`, calls target `SyncFiles`, reloads the target, verifies rebuild, and clears the rebuilding flag. `getTransferClients` also enforces controller API version 6 rebuild-concurrency limits by trimming source replica addresses.

Snapshot clone selects the first RW source replica from the source volume, requires every target replica to be RW, then concurrently calls each target sync-agent clone RPC. Snapshot hashing validates all replicas are RW, not rebuilding, and not already holding the hash lock, then fans out hash requests. Hash status is fetched concurrently and converted into a per-address status map.

### State, Persistence, And Dependencies
This file keeps no long-lived state beyond the controller client. Durable state changes happen through controller and replica-client RPCs: replica creation, mode changes, rebuild flags, disk removal markers, reloads, snapshot purge mutations, snapshot clone files, and hash checksum files. Dependencies are Longhorn controller clients, replica clients, `enginerpc`, `types`, disk naming helpers, `multierr`, and goroutine synchronization primitives.

### Integration Points
`Task` is used by CLI/API control flows that need to coordinate all replicas rather than one sync-agent. It integrates with the controller's replica list, volume start/create/prepare/verify APIs, and with per-replica sync-agent methods. It converts low-level gRPC status into JSON structs consumed by upper layers.

### Risks
Most operations are distributed fan-outs where partial success is possible. `TaskError` reports failures but cannot undo already-started replica operations. Replica clients are often opened without instance names because source replicas are chosen from controller state, so identity validation depends on volume-level context. `GetSnapshotsInfo` trusts the healthy RW replica with the largest disk map, which is pragmatic but can expose transient in-progress state as truth. Hash status appends clients from goroutines under a mutex but closes after `Wait`; future changes must preserve that ordering.

### Test Signals
Signals include tests or integration scenarios for rebuild from multiple RW sources, API-version concurrency limiting, failed source selection, rejected head-file sync lists, restore replica size mismatch, purge skip behavior for already-purging replicas, clone fan-out error aggregation, and hash lock/rebuild conflict handling. Race tests are valuable for hash status and concurrent fan-out maps.
