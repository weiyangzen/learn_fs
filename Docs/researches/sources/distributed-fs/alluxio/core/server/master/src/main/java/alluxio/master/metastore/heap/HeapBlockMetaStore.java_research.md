# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapBlockMetaStore.java

## Purpose
`HeapBlockMetaStore` is the in-memory `BlockMetaStore` implementation backed by concurrent maps. It is suitable when block metadata is kept on heap rather than in RocksDB.

## Important APIs and Types
- `mBlocks` maps block ID to `BlockMeta`.
- `mBlockLocations` is a two-key concurrent map from block ID and worker ID to `BlockLocation`.
- Implements all `BlockMetaStore` methods.
- Constructor optionally registers heap-size metrics.

## Control Flow
Block meta operations read/write/remove `mBlocks`. Location operations update `mBlockLocations` by block ID and worker ID. `getCloseableIterator` wraps the concurrent map entry iterator in a no-op-close `CloseableIterator`. `clear()` clears only `mBlocks`.

## State and Persistence
State is process-local heap memory. The class itself does not checkpoint. The block master journal/checkpoint layer must reconstruct state if needed.

## Dependencies and Integration Points
Uses `TwoKeyConcurrentMap`, protobuf block types, `MetricsSystem`, and object-size calculator. It implements the block metadata abstraction used by the block master.

## Risks and Edge Cases
- Class comment requires external synchronization for same-block operations.
- `clear()` clears block metadata but not `mBlockLocations`, which can leave stale location entries if callers expect full store reset.
- `removeBlock` also does not remove locations.
- Iterator is weakly consistent due to `ConcurrentHashMap`.

## Test Signals
Tests should cover block put/update/remove/size, location add/idempotence/remove, stale locations after block removal/clear expectations, iterator contents, and heap metric registration when enabled.
