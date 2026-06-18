# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile.go

Purpose: compiles per-bucket lifecycle rules into immutable snapshot indexes of per-action `CompiledAction` objects.

Important APIs/types: `CompileInput`, `PriorState`, `CompileOptions`, `Engine.Compile`, and `rulePredicateSensitive`. Each lifecycle XML rule expands through `s3lifecycle.RuleActionKinds` into one `ActionKey` per action kind, scoped by bucket and rule hash. `PriorState` carries durable bootstrap and mode state.

Control flow: `Compile` applies default bootstrap lookback, creates a fresh `Snapshot`, builds a `BucketIndex` per input bucket, hashes each rule, decides or preserves each action mode, determines activation, and fills indexes: bucket action keys, all actions map, date actions, original delay groups, and predicate-sensitive actions. Date actions are considered active without bootstrap rendezvous; event-driven actions require `BootstrapComplete`. Durable non-unspecified mode wins over recomputation.

State/persistence: atomically increments snapshot id and stores the snapshot in `Engine.current`. Prior states reflect durable lifecycle state; compile itself does not persist.

Dependencies/integration: uses `RuleHash`, `RuleActionKinds`, `MinTriggerAge`, `EventLogHorizon` via `decideMode`, and `SmallDelay`. Output indexes feed router matching, daily replay, bootstrap, and scheduler date scans.

Risks: duplicate `CompileInput.Bucket` entries overwrite bucket indexes. Preserving prior mode prevents accidental re-promotion, but stale modes require explicit repair. Active gating is subtle: indexes include inactive event-driven actions so `MarkActive` can work without recompilation.

Test signals: engine tests cover multi-action expansion, retention degradation, mode preservation, scan-at-date, disabled rules, cross-bucket identical rule hashes, delay group deduplication, and atomic snapshot swap.
