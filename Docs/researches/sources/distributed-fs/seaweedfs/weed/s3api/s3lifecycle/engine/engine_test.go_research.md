# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine_test.go

Purpose: exercises the compile path and core snapshot semantics.

Important helpers/tests: `ruleExpDays` builds enabled expiration rules. Tests verify single-action compile, multi-action sibling expansion, bootstrap-pending indexing but inactive status, retention gating, unbounded retention, sibling-specific degradation, durable prior mode preservation, expiration date date-actions, disabled rule behavior, `MarkActive`, cross-bucket action-key scoping, snapshot atomic swap, and delay-group deduplication across many buckets.

Control flow coverage: tests walk through mode decisions and index population, especially the difference between indexed-but-inactive event-driven actions and active scan-at-date actions. Multi-action tests ensure one XML rule produces independent action keys and delay groups.

State/persistence behavior: `PriorState` stands in for durable bootstrap/mode state. Tests confirm persisted scan-only state survives compile and does not accidentally become active.

Dependencies/integration: ties `RuleHash`, `RuleActionKinds`, `DaysToDuration`, and `CompileOptions` together.

Risks/gaps: retention-gate tests skip under shortened s3tests day units, so production-day behavior depends on normal build coverage. Tests use internal maps, which is appropriate for package-level invariants.

Test signals: strong regression coverage for identity scoping, mode preservation, delay grouping, and atomic snapshot replacement.
