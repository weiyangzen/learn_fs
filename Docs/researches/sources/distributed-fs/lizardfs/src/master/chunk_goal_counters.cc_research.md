# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.cc

Purpose: implements compact counting of file goals referencing a chunk.

Important APIs/functions: `addFile`, `removeFile`, `changeFileGoal`, `fileCount`, `highestIdGoal`.

Control flow: `addFile` validates goal IDs, finds insertion point by sorted goal, increments an existing counter unless it is at `uint8_t` max, otherwise inserts a new counter for that goal. `removeFile` finds and decrements/removes a counter or throws. `changeFileGoal` removes then adds. Query functions sum counts or return the highest sorted goal ID.

State and persistence: in-memory compact vector of `{goal,count}` records; persisted only through higher-level chunk metadata effects.

Dependencies and integration: uses `GoalId::isValid`; consumed by `chunks.cc` to compute superposed goals and metadata checksum compatibility.

Risks: `changeFileGoal` is not transaction-safe if `addFile(newGoal)` throws after removing the old one. Multiple counters per same goal are intentional when count exceeds 255.

Test signals: covered by `chunk_goal_counters_unittest.cc`, including high-count splitting and cache integration.
