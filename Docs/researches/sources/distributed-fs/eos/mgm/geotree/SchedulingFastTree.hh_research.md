# sources/distributed-fs/eos/mgm/geotree/SchedulingFastTree.hh

## Purpose
`SchedulingFastTree.hh` implements the compact, high-throughput representation used by EOS MGM geotree scheduling. Slow, mutable geotag trees are converted into these packed arrays so placement, read access, write access, draining, and gateway selection can make repeated scheduling decisions with minimal allocation and cache misses.

## Important APIs, Types, And Functions
`GeoTag2NodeIdxMap` maps hierarchical geotag strings to the closest fast-tree node using sorted child ranges and recursive binary search over geotag atoms. `FsId2NodeIdxMap<T>` maps filesystem ids to fast-tree node indexes; the `char*` specialization maps host strings for gateway lookup. Public aliases include `Fs2TreeIdxMap` and `Host2TreeIdxMap`.

Comparator and random-weight functors define scheduling policy: `PlacementPriorityComparator`, `DrainingPlacementPriorityComparator`, `ROAccessPriorityComparator`, `RWAccessPriorityComparator`, `DrainingAccessPriorityComparator`, and `GatewayPriorityComparator`, plus placement/access/gateway weight evaluators. The main template `FastTree<FsDataMemberForRand, FsAndFileDataComparerForBranchSorting, FsIdType>` stores `FastTreeNode` and `FastTreeBranch` arrays. Important methods include `selfAllocate`, `copyToBuffer`, `copyToFastTree`, `updateTree`, `updateBranch`, `sortBranchesAtNode`, `findFreeSlot`, `findFreeSlotFirstHit`, `findFreeSlotSkipSaturated`, `findFreeSlotsAll`, `decrementFreeSlot`, `disableNode`, `disableSubTree`, `checkConsistency`, and display helpers. Final typedefs instantiate placement, access, draining, and gateway trees.

## Control Flow
After `SlowTree` fills `pNodes` and `pBranches`, `updateTree()` recursively sorts every node's child branches, aggregates filesystem state upward, and aggregates file slot state upward. A placement/access operation starts at a chosen node, follows the highest-priority child branch, randomly chooses among equal-priority branches using score-derived weights, and lands on a valid leaf. When `decrFreeSlot` is true, `decrementFreeSlot()` updates leaf slot counts and walks ancestors, reordering only the modified branch with either the optimized highest-priority path or the general binary-rank/memmove path. `findFreeSlotsAll()` enumerates all valid free leaves under a subtree, optionally walking upward to a root. `findFreeSlotSkipSaturated()` explores priority levels while skipping leaves below score thresholds.

## State And Persistence
The fast tree is a mutable in-memory scheduling snapshot. Shape is fixed after build: node and branch arrays are contiguous, while file slot counters, aggregated score fields, status flags, and branch order mutate per working copy. `copyToBuffer()` supports thread-local or stack-local working copies for request handling, so scheduling can consume slots without changing the shared baseline. External metadata such as node info and id maps is referenced through pointers owned by surrounding geotree structures.

## Dependencies And Integration Points
This header depends on `SchedulingTreeCommon.hh` for state, status, comparators, and base types; on `common/utils/RandUtils.hh` for random selection; and on EOS logging. `SlowTree` and `GeoTreeEngine` are friends and populate private arrays directly. `GeoTreeEngine` uses the aliases to implement file placement, read/write replica access, draining workflows, gateway selection, disabled branches, and geotag proximity lookup.

## Risks And Edge Cases
The implementation uses raw byte allocation, pointer casting, `memcpy`, and `memmove`, so size/layout assumptions are critical. `tFastTreeIdx` is `uint16_t`; trees larger than 65535 nodes cannot be represented. `GeoTag2NodeIdxMap` truncates atoms to a small fixed tag buffer, so long geotag atoms can collide. `FsId2NodeIdxMap<T>::selfAllocate()` allocates `char[]` and later deletes through a `T*`, which is unsafe for non-char types. `findFreeSlotSkipSaturated()` declares `bool localvisited[(256)^sizeof(tFastTreeIdx)]`; `^` is bitwise XOR, not exponentiation, so the array is far smaller than the maximum tree size and can be overrun on larger trees. Many invariants are enforced only by `assert`, which may disappear in release builds.

## Test Signals
The companion test exercises construction from slow trees, placement/access round trips, closest-geotag lookup, draining placement/access, copy speed, slot decrement/repopulation, branch updates, full-tree updates, and rebuild speed. Additional high-value tests should cover saturated-node skipping on trees larger than 258 nodes, long geotag atoms, zero score weights, empty maps, disabled subtrees, capacity overflow in counters, and copy/use of every concrete typedef.
