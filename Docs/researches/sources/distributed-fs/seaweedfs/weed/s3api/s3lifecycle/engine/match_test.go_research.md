# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_test.go

Purpose: integration-style unit tests for public snapshot matching APIs.

Important helpers/tests: `activeAll` creates prior states activating every compiled action; `sortedKeys` stabilizes kind comparison. Tests verify delay-group routing for different expiration days, prefix filtering, inactive bootstrap actions becoming routable after `MarkActive`, AbortMPU matching only MPU init events, predicate changes matching only tag-sensitive rules, bootstrap `MatchPath` seeing all active actions in a multi-action rule, prefix mismatch exclusion, and nil-event `MatchPath` returning prefix-only matches despite tag filters.

Control flow/state: tests go through `Engine.Compile`, so bucket indexes, delay groups, predicate actions, and active bits are populated by production code. They distinguish event-driven matching from bootstrap/walker matching.

Dependencies/integration: integrates `RuleActionKinds`, `RuleHash`, `DaysToDuration`, and snapshot match APIs.

Risks: expected delay values must use `DaysToDuration`; hard-coded 24h values would break under s3tests build scaling. Tests validate per-kind expansion and activation, key to multi-action rule correctness.

Test signals: strong runtime-surface signal that compiled indexes route to the correct action keys and respond to activation flips.
