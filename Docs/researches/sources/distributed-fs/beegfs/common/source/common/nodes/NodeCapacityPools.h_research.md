# sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.h

## Purpose
Declares the node-oriented capacity pool abstraction used to track IDs in normal, low, and emergency capacity classes and select IDs for allocation-like workflows.

## Important APIs, Types, And Functions
The class exposes mutation, synchronization, list export, random and round-robin selection, pool lookup, state formatting, and serialization. It stores `UInt16SetVector pools`, `DynamicPoolLimits` for space and inodes, `RandomReentrant randGen`, and `lastRoundRobinTarget`.

## Control Flow
The header defines iterator ring helpers used by the implementation to walk sorted containers with wraparound and to choose a random starting point. The public serialization template emits only `pools`.

## State, Persistence, And Dependencies
The class owns an `RWLock`, pool membership, dynamic-pool configuration, random generator, and volatile round-robin cursor. It depends on `TargetCapacityPools.h` for shared capacity pool/container types, `DynamicPoolLimits`, and `RandomReentrant`.

## Integration Points
Included by `StoragePool.h` and `NodeStoreServers.h`. It mirrors `TargetCapacityPools` but lacks per-node target grouping.

## Risks
The class serializes less state than it holds; this is intentional for runtime-only cursors but important for restart behavior. Static helpers assume non-empty collections at call sites. The type accepts `uint16_t targetID` names although it may hold node IDs, which can confuse callers.

## Test Signals
Compile-time users should verify serialization compatibility and ensure client/server pool-count assumptions match `CapacityPool_END_DONTUSE`.
