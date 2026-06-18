# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters_unittest.cc

Purpose: unit tests for `ChunkGoalCounters` and its interaction with `GoalCache`.

Important tests: `Add`, `Remove`, `Change`, `LotsOfGoals`, and `Cache`.

Control flow: tests validate sorted insertion, highest-goal reporting, invalid goal/remove exceptions, count increments/decrements, counter splitting when per-counter count exceeds 255, full add/remove cycles, and LRU-like `GoalCache` insert/find/eviction behavior with counters as keys.

State and persistence: test-local data only.

Dependencies and integration: uses `common/goal.h`, `master/goal_cache.h`, `master/goal_config_loader.h`, GoogleTest, and STL helpers.

Risks: cache test uses default `Goal` values and focuses on key behavior, not semantic goal merging.

Test signals: direct regression coverage for goal counter arithmetic and cache key use.
