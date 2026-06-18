# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon.go

Purpose: computes the meta-log history horizon required to safely drive a lifecycle action from events.

Important API: `EventLogHorizon(rule, kind) time.Duration`. It returns day-derived horizons for expiration days, noncurrent days, and abort MPU; `SmallDelay` for pure count/immediate kinds (`NewerNoncurrent` without days and expired delete marker); zero for nil, undeclared, or date-based actions.

Control flow: the switch is per-action-kind rather than per-rule. Multi-action rules do not share the largest threshold across siblings, allowing independent retention gating.

State/persistence: pure function. Its output influences compile-time mode selection and may indirectly affect durable rule mode through scan-only degradation.

Dependencies/integration: uses `DaysToDuration` and `SmallDelay`; consumed by `decideMode` in the engine.

Risks: returning too small a horizon can make event-driven replay miss old due events; returning too large a horizon can unnecessarily degrade actions to scan-only. Count-only actions use `SmallDelay` because they depend on immediate state changes rather than long object age.

Test signals: `event_log_horizon_test.go` verifies per-action independence, newer-noncurrent count-only behavior, paired noncurrent-days behavior, expired marker small delay, date zero, nil zero, and undeclared zero.
