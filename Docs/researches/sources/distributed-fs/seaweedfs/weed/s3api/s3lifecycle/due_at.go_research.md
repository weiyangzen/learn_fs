# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at.go

Purpose: computes lifecycle action due times without deciding whether to dispatch now. It is used by reader/bootstrap paths to classify entries as pending or immediately eligible.

Important APIs: `DaysToDuration(days int)` converts lifecycle day thresholds through `util.LifeCycleInterval`, allowing s3tests builds to shrink days. `ComputeDueAt(rule, kind, info)` returns a zero `time.Time` when inputs, status, filters, object shape, or action kind do not allow a due time.

Control flow: after nil/status/filter checks, it switches by `ActionKind`. Abort MPU uses initiation mod time plus abort days. Expired delete marker returns marker mod time only for current sole-survivor markers. Current expiration days/date apply only to latest non-marker objects. Noncurrent days use `SuccessorModTime` or fall back to `ModTime`. Pure newer-noncurrent returns successor/mod time immediately when count-only rules apply.

State/persistence: pure function; no mutation. The due time depends on `ObjectInfo` state including latest flag, delete marker flag, version count, mtime, successor mtime, and MPU status.

Dependencies/integration: shares `filterMatches` from `evaluate.go`; depends on rule action shape and `util.LifeCycleInterval`.

Risks: `ActionKindNewerNoncurrent` due time is only a scheduling hint; final deletion still needs current ranking. Missing successor stamps fall back to legacy mtime, which can be less exact.

Test signals: `due_at_test.go` pins expiration days/date, sole-survivor delete-marker gating, undeclared kind zero, wrong object shape zero, noncurrent delete markers, successor mtime, filters, disabled rules, and MPU initiation.
