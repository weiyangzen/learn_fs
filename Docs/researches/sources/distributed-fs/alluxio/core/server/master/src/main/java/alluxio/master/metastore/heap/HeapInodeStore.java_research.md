# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapInodeStore.java

## Purpose
`HeapInodeStore` is the on-heap `InodeStore` implementation. It stores inode objects in a concurrent map and sorted parent-child edges in a two-key sorted map, with checkpoint serialization as inode protobufs.

## Important APIs and Types
- `mInodes` maps inode ID to `MutableInode<?>`.
- `mEdges` maps parent ID and child name to child ID with sorted child-name order.
- Implements inode/edge write and read methods, `allEdges`, `allInodes`, `clear`, checkpoint write/restore, and child ID iteration.
- Static `sortedMapToIterator(SortedMap<String, Long>, ReadOption)` applies `startFrom` and `prefix` filters.

## Control Flow
`writeNewInode` uses `compute` to keep an existing inode if present, logging corruption if the existing name differs. `writeInode` uses `putIfAbsent`, so it does not overwrite existing entries. Child lookups read the sorted edge map. `getChildren` maps child IDs back to inodes. Checkpoint writing emits all inode protos; restore reads inode protos and rebuilds both `mInodes` and `mEdges`.

## State and Persistence
Heap maps are volatile process state. Checkpoint type is `INODE_PROTOS`, and checkpoint name is `HEAP_INODE_STORE`. Restoring from checkpoint reconstructs parent-child edges from each inode's parent ID/name.

## Dependencies and Integration Points
Depends on `TwoKeyConcurrentSortedMap`, inode metadata classes, `ReadOption`, checkpoint streams, metrics, and object-size calculation. It is a backing or standalone inode store for the file master.

## Risks and Edge Cases
- `writeInode` not overwriting existing inode metadata may be surprising for updates; callers must rely on mutating existing mutable inode objects or use implementation-specific expectations.
- Restoring root or special parent IDs into the edge map depends on inode proto parent fields.
- `sortedMapToIterator` prefix/start comparisons must match RocksDB behavior for cross-store consistency.
- Concurrent sorted-map iteration is weakly consistent.

## Test Signals
Tests should cover write-new conflict logging, write/update semantics, sorted listing with start/prefix combinations, checkpoint round-trip, edge rebuild on restore, clear behavior, and heap metrics.
