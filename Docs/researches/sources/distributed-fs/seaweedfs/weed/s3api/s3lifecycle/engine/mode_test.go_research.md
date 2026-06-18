# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode_test.go

Purpose: validates default rule mode decisions and mode string labels.

Important tests: nil and disabled rules resolve to disabled; expiration-date actions resolve to scan-at-date; unbounded retention uses event-driven; horizons within retention remain event-driven; horizons exceeding retention become scan-only; bootstrap lookback can push a rule across the threshold; zero horizons do not gate; `RuleMode.String` renders documented names and falls back to `unspecified`.

Control flow/state: direct calls to `decideMode` isolate mode policy from compile indexing. Tests use lifecycle rules with expiration days and dates plus retention/lookback durations.

Dependencies/integration: depends on `EventLogHorizon`, `DaysToDuration`, and `SmallDelay` semantics.

Risks/gaps: package-private testing is appropriate, but durable prior mode preservation is covered in compile tests rather than here. Time-scaling build tags can affect threshold expectations, so tests choose durations through lifecycle helpers.

Test signals: good policy-level signal for retention gate regressions and operator-visible string labels.
