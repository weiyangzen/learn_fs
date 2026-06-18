# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule.go

## Purpose
This file defines the canonical flat lifecycle rule and object-evaluation data structures shared across the lifecycle compiler, router, evaluator, scheduler, and tests.

## Important APIs and types
`Rule` represents XML-derived lifecycle configuration after canonicalization. It includes rule identity/status, prefix, current expiration by days or date, expired delete marker flag, noncurrent expiration days, `NewerNoncurrentVersions`, abort-MPU days, tag filters, and size filters. `ObjectInfo` describes a candidate object or MPU init event: key, modification time, size, current/delete-marker state, version count, successor modification time, optional noncurrent rank, tags, and MPU-init marker. Constants define enabled/disabled statuses, `SmallDelay`, action enum values, and `EvalResult`.

## Control flow and state behavior
The file has no executable control flow and no persistence. Its field semantics drive other packages: zero values generally mean unset, `NoncurrentIndex` is a pointer so rank zero is distinguishable from unknown, and `SuccessorModTime` is the clock for noncurrent retention.

## Dependencies and integration points
The only direct dependency is `time`. The structures are populated by XML parsing/canonicalization, router event classification, bootstrap version walking, and S3 Tables-independent lifecycle evaluation code. `RuleHash`, `RuleActionKinds`, `ComputeDueAt`, and `EvaluateAction` depend on these fields.

## Risks and edge cases
`FilterSizeGreaterThan` cannot represent an explicit greater-than-zero exclusion differently from unset zero, as noted in the comment. Misinterpreting zero-valued days, dates, rank pointers, or MPU flags can produce immediate or wrong-kind actions. Because this is a shared schema, adding fields requires updating hashing, evaluation, XML canonicalization, and tests.

## Test signals
This file has no direct tests, but its fields are exercised by rule hash tests, router tests, config-load tests, and evaluator/compiler tests elsewhere in the package tree.
