# sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.h

## Purpose
Declares the target capacity-pool model, including plain target pools and node-grouped pools for failure-domain-aware selection.

## Important APIs, Types, And Functions
Defines `TargetMap`, `GroupedTargets`, `GroupedTargetsVector`, and class `TargetCapacityPools`. Public APIs cover mutation, sync, selection, inter/intra-domain placement, pool lookup, state dump, string conversion, and serialization.

## Control Flow
Private helpers implement unlocked add/update, removal from other pools, plain/preferred selection, interdomain/intradomain selection, grouping by node, stripping used nodes, and target-to-node lookup.

## State, Persistence, And Dependencies
The class owns an `RWLock`, dynamic config, plain pools, grouped pools, target map, random generator, and round-robin cursor. Serialization covers placement-critical membership and mapping state.

## Integration Points
Used by `StoragePool` and storage target placement. Shares `CapacityPoolType`/`DynamicPoolLimits` concepts with `NodeCapacityPools`.

## Risks
The header documents that not all targets may be in grouped pools if mapping is unknown. Selection helpers assume caller-held locks and non-empty inputs.

## Test Signals
Compile-time and serialization tests should ensure grouped types remain stable and that client/server capacity pool counts align.
