# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate_test.go

Purpose: comprehensive tests for lifecycle action evaluation.

Important helpers/tests: `idx` creates noncurrent indexes and `mustTime` parses fixed UTC times. Tests cover nil/disabled no-ops, expiration-day boundary at due time, undeclared action kinds, multi-action sibling independence, expiration date, expired delete marker sole-survivor behavior, noncurrent delete markers under noncurrent days, successor-time due math, fallback to mod time, keep-N nil-index no-op, pure newer-noncurrent count thresholds, combined noncurrent days plus keep-N, abort MPU boundaries, prefix/tag/size filters, empty prefix, and MPU init suppression for noncurrent kinds.

Control flow/state: tests populate `ObjectInfo` fields representing live and bootstrap-derived state. Boundary checks use `now.Before(due)` semantics, so equality fires.

Dependencies/integration: covers `filterMatches` through public evaluation and shares `DaysToDuration` for build-tag-safe day math.

Risks/gaps: tests do not inspect `RuleID` for every firing action, but boundary and action mapping are well covered. The nil-index safety tests document intentional no-op behavior for pointer migration and ranking gaps.

Test signals: high-confidence behavioral signal for deletion eligibility and safety gates.
