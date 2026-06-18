# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/BlockMetaStore.java

## Purpose
`BlockMetaStore` defines the master-side storage contract for block metadata and block locations. It abstracts heap and RocksDB implementations used by the block master.

## Important APIs and Types
- `getBlock`, `putBlock`, and `removeBlock` manage `BlockMeta` by block ID.
- `getLocations`, `addLocation`, and `removeLocation` manage `BlockLocation` entries by block ID and worker ID.
- `clear`, `close`, and `size` provide lifecycle and accounting operations.
- `getCloseableIterator()` returns a closeable iterator over `Block` objects and explicitly documents that callers must close it.
- Nested `Block` holds an ID and `BlockMeta`.
- Nested `Factory extends Supplier<BlockMetaStore>`.

## Control Flow
The interface imposes no implementation flow, but the contract expects block metadata operations and location operations to be available independently. Iteration clients use try-with-resources to avoid leaking backend resources.

## State and Persistence
State is implementation-specific. `HeapBlockMetaStore` keeps concurrent maps in memory; `RocksBlockMetaStore` persists in RocksDB column families and supports checkpointing through `RocksCheckpointed`.

## Dependencies and Integration Points
Uses protobuf `BlockMeta`/`BlockLocation` and `CloseableIterator`. It is consumed by block master metadata management, block integrity scans, and journal/checkpoint dumping.

## Risks and Edge Cases
- Interface does not require atomic coupling between block metadata and locations; callers must handle consistency.
- `removeBlock` contract says nothing about clearing locations; implementation behavior differs and callers must know whether orphaned locations are possible.
- Iterator leaks are explicitly called out as a risk.

## Test Signals
Shared implementation tests should cover put/update/remove, no-op removals, duplicate location add behavior, location removal by worker, clear/size, and iterator closure.
