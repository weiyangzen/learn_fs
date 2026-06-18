# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes_test.go

Purpose: validates replay and promotion hash contracts used by cursor recovery logic.

Important tests: nil/walker-only snapshots produce empty replay hashes; replay content hash remains stable when retention partition changes; TTL edits change replay content; rule order does not affect hash; walker-only and disabled additions are excluded. Promotion tests cover empty when nothing is promoted, replay-to-walk and walk-to-replay changes, stability for unchanged partition, and membership agreement with `RulesForShard`. Max TTL tests cover nil/empty, max across replay actions, replay-view-only behavior, and inactive action exclusion.

Control flow/state: tests build snapshots through `buildSnapshotForViews`, ensuring compile indexes and prior bootstrap state are realistic. Hashes are compared as value outputs; no mutation.

Dependencies/integration: depends on `RulesForShard` and `DaysToDuration` to prove hash semantics align with runtime partitioning.

Risks/gaps: `PromotedHash_MatchesRulesForShardWalkMembership` checks non-empty/hash behavior rather than decoding hash contents, which is expected for SHA outputs but means exact item list is inferred from partition setup.

Test signals: high-value regression signal for recovery correctness; accidental ordering drift, disabled-rule inclusion, or retention predicate mismatch should fail these tests.
