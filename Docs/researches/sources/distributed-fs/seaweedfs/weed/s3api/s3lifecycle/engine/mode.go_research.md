# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode.go

Purpose: defines lifecycle rule execution modes and the default mode decision policy.

Important APIs/types: `RuleMode` enum, `String`, and `decideMode`. Modes include unspecified, event-driven, scan-at-date, scan-only, disabled, and pending-bootstrap. String rendering is used in logs/metrics/state bridges.

Control flow: `decideMode` returns disabled for nil or disabled rules. Expiration-date actions are scan-at-date. Other actions are event-driven unless `MetaLogRetention` is positive and less than `EventLogHorizon(rule, kind) + bootstrapLookbackMin`, in which case they become scan-only. Retention 0 means unbounded and never gates.

State/persistence: no persistence directly, but `RuleMode` mirrors durable protobuf lifecycle state. Compile may preserve durable prior mode over `decideMode`.

Dependencies/integration: calls `s3lifecycle.EventLogHorizon` and consumes `ActionKind`. Scheduler, daily replay, and bootstrap use modes to select event-driven, date-scan, or scan-only paths.

Risks: retention math is sensitive to build-tag day scaling and lookback margin. Unknown enum values stringify as `unspecified`, which avoids empty labels but can hide unexpected durable values if not logged with numeric context elsewhere.

Test signals: `mode_test.go` covers nil/disabled, date mode, unbounded retention, retention threshold boundaries, lookback effects, zero horizon, and string rendering including unknown values.
