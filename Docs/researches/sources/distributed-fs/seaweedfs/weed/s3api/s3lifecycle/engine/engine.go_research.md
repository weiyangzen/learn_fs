# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine.go

Purpose: defines the core engine and snapshot data model used by lifecycle routing.

Important APIs/types: `Engine`, `New`, `Snapshot`, `BucketIndex`, `CompiledAction`, `SnapshotID`, `Action`, `AllActions`, `OriginalDelayGroups`, `PredicateActions`, `DateActions`, `BucketVersioned`, `BucketActionKeys`, and `MarkActive`. `CompiledAction` contains the rule pointer, bucket, action key, delay, predicate sensitivity, mode, and atomic active bit.

Control flow: `New` installs an empty snapshot. `Snapshot` returns the atomically current snapshot. Accessors either return direct immutable data (`Action`, `AllActions`) or defensive copies for mutable maps/slices. `MarkActive` flips the atomic active state when a key exists and silently ignores stale keys.

State/persistence: in-memory snapshots are swapped atomically by compile. The only post-compile mutation is per-action `engineState`, used to activate event-driven actions after durable bootstrap completion.

Dependencies/integration: used by router, dispatcher, daily-run partitioning, and tests. `ActionKey` from `s3lifecycle` is the identity key.

Risks: `AllActions` returns the internal sorted slice by design, so callers must not mutate. Bucket/action maps are otherwise shared read-only. `MarkActive` races are deliberately tolerated but only affect the current snapshot object receiving the call.

Test signals: snapshot accessor tests cover defensive copies, activation, unknown-key no-op, bucket versioned flags, action key coverage, all-action enumeration, and monotonic snapshot ids.
