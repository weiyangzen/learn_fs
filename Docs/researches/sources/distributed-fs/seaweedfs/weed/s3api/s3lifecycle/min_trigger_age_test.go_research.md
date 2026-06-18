# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age_test.go

Purpose: validates per-kind trigger-age extraction.

Important tests: a rule with expiration days, noncurrent days, and abort MPU returns each respective `DaysToDuration`; expiration date, newer noncurrent, and expired delete marker return zero. Asking a kind not set on the rule returns zero. Date-only rules and nil rules return zero.

Control flow/state: direct pure-function tests; no mutable state.

Dependencies/integration: uses `DaysToDuration` for build-tag-safe expectations and `mustTime` for date-only setup.

Risks/gaps: tests cover positive thresholds but not explicitly zero/negative threshold fields for day kinds; production XML parsing likely prevents negative values, and zero is implicitly covered by date/kind-not-set cases.

Test signals: focused branch-level signal for compile delay grouping and safety-scan cadence inputs.
