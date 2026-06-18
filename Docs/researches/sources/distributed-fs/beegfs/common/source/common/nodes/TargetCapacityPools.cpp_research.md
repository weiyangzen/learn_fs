# sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.cpp

## Purpose
Implements target capacity pools with both plain target membership and target grouping by owning node, enabling random placement as well as inter-domain and intra-domain placement choices.

## Important APIs, Types, And Functions
Implements add/update/remove/sync/list export, `chooseStorageTargets()`, `chooseStorageTargetsRoundRobin()`, `chooseTargetsInterdomain()`, `chooseTargetsIntradomain()`, grouping helpers, pool lookup, state formatting, and pool-type string conversion.

## Control Flow
Mutation updates `pools`, `groupedTargetPools`, and `targetMap` under write lock. Sync builds temporary plain and grouped pools outside the write-lock section and swaps them in. Normal target selection tries normal, low, then emergency pools, with optional preferred-target stages. Interdomain selection chooses one random target from each selected node group and strips already-used nodes when falling through to lower pools. Intradomain selection chooses one random node group and then targets within that same group. Round-robin uses `lastRoundRobinTarget`.

## State, Persistence, And Dependencies
State is `pools`, `groupedTargetPools`, `targetMap`, dynamic pool limits, random generator, and round-robin cursor. Serialization includes `pools`, `groupedTargetPools`, and `targetMap`, but not the cursor or dynamic-limit config. It depends on `TargetMapper` types, `RWLockGuard`, `MinMaxStore`, `DynamicPoolLimits`, `NumNodeID`, and common containers.

## Integration Points
`StoragePool` owns one for its targets. `TargetMapper` and storage-pool management feed target-to-node mappings. File placement and mirror selection can request ordinary, interdomain, or intradomain target sets.

## Risks
Targets without node mappings are omitted from grouped pools, so inter/intra-domain selectors can see fewer targets than plain selectors. A condition in preferred selection reads `if (!outTargets->empty() >= minNumRequiredTargets)`, comparing a boolean with the threshold and likely not doing what the comment intends. Inter/intra-domain methods note they do not try hard to satisfy `minNumRequiredTargets`. Round-robin state is not persisted. Callers must avoid `numTargets == 0` before helpers compute `activeTargetsSize / numTargets`.

## Test Signals
Test target movement between pools and nodes, grouped map cleanup, sync with missing target mappings, preferred target fallback, the suspicious boolean comparison, interdomain uniqueness, intradomain same-node behavior, round-robin wraparound, empty/zero target requests, and serialization round trips.
