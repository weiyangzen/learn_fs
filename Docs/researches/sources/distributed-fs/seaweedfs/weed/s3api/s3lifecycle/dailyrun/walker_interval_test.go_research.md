# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_interval_test.go

Purpose: tests walker throttle semantics, validation of negative intervals, and prevention of double full-bucket walks in one shard pass.

Important APIs/types: `readerEventAlias`, `TestWalkerDue`, `TestRunShard_WalkerThrottle`, `validatableConfig`, stubs for config validation, `TestRunShard_ColdStartDoesNotDoubleWalk`, and `TestRunShard_RecoveryWalkerSetsLastWalkedAnchor`.

Control flow: `TestWalkerDue` covers pure throttle decisions. `TestRunShard_WalkerThrottle` pre-seeds matching cursors, forces a walk partition with tiny retention, runs two passes with closed event channels, and checks call counts/`LastWalkedNs`. Validation test constructs a minimal valid config and rejects negative intervals. Cold-start and recovery tests call `runShard` directly to assert one walker call and anchor updates.

State and persistence behavior: in-memory cursor state is central. Tests validate `LastWalkedNs` as the persisted throttle anchor and ensure cold-start/recovery walker fires update it.

Dependencies and integration points: uses engine snapshots, in-memory persister, lifecycle shard count, reader event channel typing, and config validation stubs.

Risks: direct `runShard` tests bypass `validate`, so configs omit fields that `Run` requires. Comments document some test sentinels (`RetentionWindow`) that rely on implementation details. Wall-clock is controlled by injected `runNow`, which is good.

Test signals: strong regression coverage for avoiding excessive filer load from repeated full walks while preserving default interval-zero behavior.
