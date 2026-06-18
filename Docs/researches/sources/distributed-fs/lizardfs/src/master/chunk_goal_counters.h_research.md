# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.h

Purpose: declares `ChunkGoalCounters`, the compact data structure for calculating the superposition of goals for shared chunks.

Important APIs/types/functions: `GoalCounter { uint8_t goal; uint8_t count; }`, `Counters = compact_vector<GoalCounter>`, iterators, `InvalidOperation`, `addFile`, `removeFile`, `changeFileGoal`, `fileCount`, `highestIdGoal`, `size`, and `clear`.

Control flow: callers update counters as files are added, removed, or change goal; iteration exposes sorted counters for goal merging/cache keys.

State and persistence: owns compact in-memory counter vector.

Dependencies and integration: depends on `common/compact_vector.h` and exception helpers; used by chunk metadata and `GoalCache`.

Risks: counter count is `uint8_t`, requiring duplicate entries for high counts; all consumers must treat repeated goals correctly.

Test signals: `chunk_goal_counters_unittest.cc`.
