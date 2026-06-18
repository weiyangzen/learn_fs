# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age.go

Purpose: returns the day-style minimum trigger age for a specific lifecycle action kind.

Important API: `MinTriggerAge(rule, kind) time.Duration`. It returns `DaysToDuration` for expiration days, noncurrent days, and abort MPU when the matching threshold is positive; otherwise zero.

Control flow: nil rule returns zero. Date, count-only, expired delete marker, undeclared kinds, and non-positive thresholds all return zero. The function is per-kind and does not choose a maximum across a multi-action rule.

State/persistence: pure function. Output is stored in compiled actions as `Delay` and used by safety-scan cadence and original-write delay grouping.

Dependencies/integration: used by `engine.Compile`, snapshot delay groups, and tests; depends on `DaysToDuration`.

Risks: returning a non-zero delay for date/count/immediate actions would incorrectly place them in original-write delay groups. Returning zero for declared day actions would over-poll or mispartition dispatch paths.

Test signals: `min_trigger_age_test.go` covers per-kind values, undeclared kind zero, date-only zero, and nil rule zero.
