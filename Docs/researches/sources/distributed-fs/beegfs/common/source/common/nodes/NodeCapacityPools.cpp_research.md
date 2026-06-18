# sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.cpp

## Purpose
Implements `NodeCapacityPools`, a thread-safe three-pool selector for numeric node IDs. BeeGFS reuses this class for metadata-server capacity pools and buddy-group IDs, where only plain membership and random/round-robin selection are needed.

## Important APIs, Types, And Functions
`addOrUpdate()`, `addIfNotExists()`, `remove()`, `syncPoolsFromLists()`, `syncPoolsFromSets()`, `getPoolsAsLists()`, `chooseStorageTargets()`, `chooseStorageTargetsRoundRobin()`, `getPoolAssignment()`, `getStateAsStr()`, and `poolTypeToStr()` are the public behavior implemented here. Private helpers remove IDs from other pools and choose targets with or without preferences.

## Control Flow
Writes take the `RWLock` in write mode and maintain the invariant that one ID appears in at most one `CapacityPoolType`. `addIfNotExists()` uses a read-lock fast path, then rechecks under write lock before inserting. `chooseStorageTargets()` prefers normal, then low, then emergency pools; with preferred targets, it first tries preferred normal/low entries, then non-preferred normal/low entries, then emergency. Non-preferred selection divides the sorted set into ranges and picks one random element from each range. Round-robin selection uses `lastRoundRobinTarget` and requires a write lock.

## State, Persistence, And Dependencies
State is in-memory: `pools`, `lastRoundRobinTarget`, dynamic-pool flags/limits, and a `RandomReentrant`. Serialization only covers `pools`; round-robin position and dynamic limit values are constructor-owned runtime configuration. Dependencies include `RWLockGuard`, `DynamicPoolLimits`, `CapacityPoolType`, and common BeeGFS UInt16 containers.

## Integration Points
`StoragePool` uses this class for buddy capacity pools. `NodeStoreServers` can attach a `NodeCapacityPools` and removes node IDs from it on node deletion. Management and metadata placement code consume `getPoolsAsLists()` and `chooseStorageTargets()`.

## Risks
Callers must pass a correctly sized `UInt16ListVector`/`UInt16SetVector`; there are no explicit bounds checks before indexing by pool type. The chooser can return fewer than requested targets, so callers must honor `minNumRequiredTargets`. Round-robin state is not persisted and is intentionally global across pools. Preferred-target fallback stops early once any preferred target is found in some paths, which can produce fewer than the requested count.

## Test Signals
Tests should cover pool movement uniqueness, fast-path duplicate insert, list/set sync, empty pools, normal-to-low-to-emergency fallback, preferred target filtering, duplicate preferred IDs, round-robin wraparound, serialization of pools, and concurrent add/remove/select under lock instrumentation.
