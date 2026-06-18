# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/log_startup_test.go

Purpose: executes `Reader.LogStartup` branches for compile-time and panic-safety coverage.

Important tests: single-shard `ShardID` logging; shard-predicate/range logging; explicit `StartTsNs` overriding cursor min; cursor min fallback when `StartTsNs` is zero.

Control flow/state: tests do not assert log output, only that the helper runs through each branch without panic. Cursor state may be empty.

Dependencies/integration: `LogStartup` writes through SeaweedFS glog. It is used by worker startup for a one-line resume summary.

Risks/gaps: no log-capture assertion means format changes are not pinned; this is acceptable because behavior is diagnostic, not functional. The tests mainly prevent branch rot and nil dereferences.

Test signals: light coverage for logging paths and resume-position selection in log context.
