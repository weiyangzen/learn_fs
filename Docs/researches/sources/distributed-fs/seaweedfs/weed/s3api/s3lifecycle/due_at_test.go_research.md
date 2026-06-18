# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at_test.go

Purpose: verifies `ComputeDueAt` as the scheduling-time companion to `EvaluateAction`.

Important test cases: expiration by days adds `DaysToDuration`; expiration by date returns the configured date; expired delete marker returns zero when not the sole survivor; undeclared action kinds and wrong object shapes return zero. Noncurrent delete markers are treated as normal noncurrent versions under noncurrent-days rules. Noncurrent due time prefers `SuccessorModTime`; filters and disabled status suppress due times; MPU init records use abort days from initiation mtime.

Control flow coverage: tests exercise every switch branch with both positive and negative paths. They also show that kind/action matching is strict; asking an abort-MPU kind of an expiration-only rule cannot synthesize a due time.

State/persistence behavior: no persisted state, but tests model `ObjectInfo` fields that come from entry metadata, sibling scans, and bootstrap expansion.

Dependencies/integration: reuses `mustTime` from `evaluate_test.go` and lifecycle rule structs.

Risks: because `DaysToDuration` is build-tag-scaled, tests compare to that helper rather than hard-coded 24h days. Missing direct test for pure `ActionKindNewerNoncurrent` due time is a residual gap, though evaluation tests cover deletion behavior.

Test signals: strong branch-level signal for due-date math and filter/status gates.
