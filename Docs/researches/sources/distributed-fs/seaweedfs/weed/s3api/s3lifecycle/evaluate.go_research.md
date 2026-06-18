# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate.go

Purpose: evaluates whether a lifecycle rule action should fire for an object at a specific time.

Important API: `EvaluateAction(rule, kind, info, now) EvalResult` and helper `filterMatches`. It returns `ActionNone` for nil/disabled/nonmatching inputs and maps eligible actions to lifecycle dispatcher actions such as delete object, delete version, expire delete marker, and abort MPU.

Control flow: the function filters by status and rule filters, suppresses all non-abort actions for MPU-init records, then switches by action kind. Current expiration days/date require latest non-marker objects and due time. Expired object delete marker requires current sole-survivor marker. Noncurrent days require non-latest plus due time; if keep-N is configured, nil index or too-new index suppresses deletion. Pure newer-noncurrent is count-only and requires an index at or beyond keep count.

State/persistence: pure function over `Rule`, `ObjectInfo`, and `now`. It relies on caller-provided version ranking and successor timestamps derived from metadata or sibling scans.

Dependencies/integration: used by router/bootstrap/daily-run dispatch before issuing deletes. `filterMatches` implements prefix, strict size, and tag-equality filters and is also used by `ComputeDueAt`.

Risks: nil `NoncurrentIndex` is safety-critical; guessing would delete retained versions. MPU-init records have `IsLatest=false`, so the explicit guard prevents noncurrent actions from freezing dispatcher cursors on empty version ids.

Test signals: `evaluate_test.go` covers branch boundaries, multi-action independence, filters, noncurrent markers, keep-N semantics, nil-index safety, and MPU guard.
