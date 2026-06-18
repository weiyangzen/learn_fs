# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon_test.go

Purpose: verifies action-specific event-log horizon calculations.

Important tests: multi-action rules produce independent horizons for expiration days, abort MPU, and noncurrent days; expiration-date returns zero. Pure newer-noncurrent returns `SmallDelay`, but when paired with noncurrent days the newer-noncurrent kind is not considered declared and returns zero while noncurrent-days carries the day horizon. Expired delete marker returns `SmallDelay`. Nil rules and undeclared kinds return zero.

Control flow/state: direct pure-function calls over rule structs. No persistent state.

Dependencies/integration: validates values used by engine mode decisions and retention gate tests.

Risks/gaps: tests assume action-kind expansion logic elsewhere will not create a `NewerNoncurrent` action when noncurrent days is set; that is tested in action-kind/rule tests outside this work item.

Test signals: good focused coverage for a small function whose incorrect output could silently alter event-driven versus scan-only behavior.
