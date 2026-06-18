# sources/distributed-fs/lizardfs/src/master/goal_cache.h

Purpose: defines an LRU cache mapping chunk goal-counter summaries to resolved `Goal` objects.

Important APIs/types/functions: `CountersHasher` hashes only each `GoalCounter::goal`; `CountersComparator` compares counter-vector size and goal ids, also ignoring counts; `GoalCache` aliases `GenericLruCache<ChunkGoalCounters, Goal, 0x10000, ...>`.

Control flow: callers can cache goal resolution keyed by the set/order of goal ids present in `ChunkGoalCounters`.

State and persistence behavior: cache state is transient in memory and capped at 65,536 entries. It is not persisted.

Dependencies/integration: depends on `GenericLruCache` and `ChunkGoalCounters`. Used by master chunk/goal computation paths to avoid rebuilding goals for repeated counter patterns.

Risks and test signals: comparator ignores counts and only compares goal ids, which is correct only if resolved `Goal` depends solely on the goal-id sequence rather than counts. Tests should verify cache hits/misses for same goal ids with different counters and confirm that this intentional key reduction is valid.
