# sources/distributed-fs/lizardfs/src/data/mfsgoals.cfg

Purpose: sample goal definition file for replication and erasure-code placement goals.

Important syntax: `<goal id> <name-or-count> : <labels>` for standard copies, plus examples of special goals such as `$xorN` and `$ec(k,m)` with optional label constraints.

Control flow: master goal loader reads active goals to map file goal IDs to desired chunk-part layouts and media-label placement. Default goals 1-5 are active in this example; unspecified goals fall back to `min(goal_id, 5)` standard copies.

State and persistence: persistent cluster placement policy; affects chunk replication/rebalancing and file goal semantics after reload.

Dependencies and integration: installed as a master example and referenced by `CUSTOM_GOALS_FILENAME`; consumed by chunk placement, `ChunkGoalCounters`, `GoalCache`, and `ChunkCopiesCalculator`.

Risks: changing goal IDs or labels changes placement behavior for files using those goals. Examples show duplicate IDs in comments, which are illustrative but could be copied incorrectly.

Test signals: goal/counter behavior is indirectly covered by `chunk_goal_counters_unittest.cc` and broader goal loader tests outside this subset.
