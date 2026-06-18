# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile_helpers_test.go

Purpose: direct unit coverage for `rulePredicateSensitive`, the helper that decides whether a rule should be indexed for predicate-change events.

Important cases: nil rules return false defensively; rules with no `FilterTags` return false; non-nil but empty tag maps return false; populated tag filters return true.

Control flow/state: no runtime state. The helper is intentionally tag-only: size filters are immutable after object write, while tags in the entry `Extended` metadata can change without resetting object mtime.

Dependencies/integration: imports `s3lifecycle.Rule` and testify. `Compile` uses this helper to fill `CompiledAction.PredicateSensitive` and append action keys to `Snapshot.predicateActions` when mode is event-driven.

Risks: if future mutable predicates are added beyond tags, this helper must be updated or predicate-change routing will miss them. Conversely, over-classifying immutable predicates would waste routing work but not usually affect correctness.

Test signals: focused branch coverage for a small but routing-sensitive helper; broader match tests verify `PredicateActions` and `MatchPredicateChange` behavior end to end.
