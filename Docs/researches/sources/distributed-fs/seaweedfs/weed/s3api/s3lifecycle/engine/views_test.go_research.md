# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views_test.go

Purpose: validates snapshot view construction for replay, walk, and recovery paths.

Important helpers/tests: `buildSnapshotForViews` compiles active snapshots. Tests cover nil/current engine behavior, nil snapshot partitioning, replay membership for day-based/MPU actions, walk-only kinds, multi-action rules split across replay/walk, scan-only promotion when TTL exceeds retention, replay forcing `ModeEventDriven` on rehabilitated scan-only actions, disabled exclusion, clone independence from base actions, zero retention routing replay kinds to walk, recovery activation of inactive actions, preserving scan-at-date mode, disabled exclusion in recovery, and recovery clone independence.

Control flow/state: tests inspect per-view action maps and active bits. They deliberately mutate clone active state to prove atomics are not shared with base actions.

Dependencies/integration: ties `RulesForShard`, `RecoveryView`, compile prior state, and retention windows together.

Risks/gaps: `shardID` is not behaviorally tested because current implementation ignores it by design. Package-level current engine tests save and restore global pointer to avoid cross-test pollution.

Test signals: strong coverage for safe partitioning and recovery semantics, especially retention loss and mode rehabilitation behavior.
