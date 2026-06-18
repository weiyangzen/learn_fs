# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes.go

Purpose: computes stable hashes that daily replay cursors use to detect rule-content changes and retention partition flips.

Important APIs: `ReplayContentHash`, `PromotedHash`, and `MaxEffectiveTTL`. Internal helpers include `hashItem`, `sortHashItems`, `hashWriter`, and `effectiveTTL` from `views.go`.

Control flow: both hash functions collect non-disabled replay-eligible actions, sort by rule hash, action kind, and bucket, then write varint-tagged fields into SHA-256. `ReplayContentHash` includes bucket, rule hash, action kind, and effective TTL, but intentionally ignores whether an action is currently replay or walk. `PromotedHash` includes replay-eligible actions that would land in walk for a retention window. `MaxEffectiveTTL` scans active replay-eligible actions and returns the maximum effective TTL.

State/persistence: pure computations over snapshots. Their outputs are intended for persisted cursor metadata; mismatches trigger recovery paths.

Dependencies/integration: depends on `Snapshot.actions`, `RuleMode`, `ActionKind`, and replay partition rules. It must match `RulesForShard` membership exactly for promoted actions.

Risks: hash schema changes affect persisted cursors. `PromotedHash` with retention 0 treats all replay-eligible actions as promoted, matching safe walk-only behavior. Disabled and walker-only actions are excluded from replay content.

Test signals: `hashes_test.go` verifies empty cases, partition independence, content edits, rule reorder stability, disabled/walker exclusion, promoted hash flips both directions, agreement with `RulesForShard`, and max TTL behavior.
