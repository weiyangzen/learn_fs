# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksBlockMetaStore.java

## Purpose
`RocksBlockMetaStore` is the RocksDB-backed `BlockMetaStore` implementation. It stores block metadata and block locations in separate RocksDB column families, exposes RocksDB operational metrics, and participates in checkpoint/restore through `RocksCheckpointed`.

## Important APIs and Types
- Implements `BlockMetaStore` and `RocksCheckpointed`.
- Uses column families `block-meta` and `block-locations` under database name `blocks`.
- Holds `WriteOptions mDisableWAL`, prefix/iterator `ReadOptions`, `RocksStore`, column handle references, `mToClose`, and `LongAdder mSize`.
- Public methods implement block CRUD, location CRUD, iteration, clear, close, size, `getRocksStore`, and `getCheckpointName`.

## Control Flow
Construction loads the RocksDB native library, configures options either from a Rocks config file or built-in column-family options, applies table-cache/bloom/index settings from Alluxio properties, creates the Rocks store, and registers many cached Rocks property gauges. Reads and writes acquire `RocksStore` shared locks. `putBlock` checks prior existence to increment `mSize`, writes with WAL disabled, and overwrites existing metadata. `removeBlock` decrements size if the key existed. `getLocations` uses prefix iteration over block-location keys. Full block iteration uses `RocksUtils.createCloseableIterator` and abort checks.

## State and Persistence
Block metadata and locations persist in RocksDB. `mSize` is in-memory accounting updated by put/remove and reset by clear/close; it is not rebuilt in this file after restore. Checkpoint name is `BLOCK_MASTER`, and checkpoint bytes are produced by `RocksStore`.

## Dependencies and Integration Points
Depends on RocksDB Java APIs, `RocksStore`, `RocksUtils`, `RocksCheckpointed`, Alluxio configuration, metrics, protobuf block types, and path/file utilities. It is used by the block master when Rocks metastore is enabled.

## Risks and Edge Cases
- WAL is disabled, so durability relies on Alluxio journal/checkpoint semantics rather than Rocks WAL.
- `getLocations` iterates with prefix-same-as-start and assumes one block has bounded locations.
- `removeBlock` does not remove block-location records.
- `mSize` can become inaccurate if state is restored or externally modified without replaying put/remove accounting.
- Native RocksDB resources must be closed in reverse order after taking the exclusive close lock.

## Test Signals
Tests should cover column-family config validation, put/remove size accounting, location prefix iteration, clear resetting Rocks and size, checkpoint/restore via `RocksCheckpointed`, close resource order, Rocks property gauges, and iterator abort behavior during close/rewrite.
