# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksInodeStore.java

## Purpose
`RocksInodeStore` is the RocksDB-backed `InodeStore` implementation. It stores inode protobufs and parent-child edges in separate column families, supports prefix/range listing, batch writes, checkpoints, and RocksDB memory/health metrics.

## Important APIs and Types
- Implements `InodeStore` and `RocksCheckpointed`.
- Uses database name `inodes` and columns `inodes` and `edges`.
- Uses key encoding: inode IDs as 8-byte longs; edge keys as parent ID bytes followed by child name bytes.
- Public methods cover inode CRUD, edge CRUD, mutable/read-only child lookup, child ID iteration, `hasChildren`, full debug sets, closeable inode iteration, batch writes, clear, close, checkpoint name, and RocksStore access.
- Inner `RocksIter` iterates child IDs while enforcing optional child-name prefix.
- Inner `RocksWriteBatch` batches inode/edge puts/deletes and commits via RocksDB write batch.

## Control Flow
Construction configures RocksDB options from an optional config file or default hash memtable/prefix extractor setup, applies table config properties, initializes `RocksStore`, and registers many RocksDB gauges plus aggregate memory gauges. Each normal operation acquires a `RocksSharedLockHandle`. Child iteration creates a Rocks iterator, seeks to parent/prefix/start key, then returns a closeable iterator holding a second shared lock for the lifetime of iteration; each `next` checks whether RocksDB has been closed or rewritten. `getChild` warns if an edge points to a missing inode. `clear` uses rewrite exclusive locking. Close uses closing exclusive lock and closes Rocks objects in reverse order.

## State and Persistence
Inodes and edges persist in RocksDB. WAL is disabled, so persistence is coordinated by Alluxio journal/checkpoint. Checkpoint name is `ROCKS_INODE_STORE`; checkpoint/restore is inherited from `RocksCheckpointed`. Full iteration and all-inode/all-edge debugging read from RocksDB using total-order seek.

## Dependencies and Integration Points
Depends on RocksDB Java APIs, `RocksStore`, `RocksUtils`, `ReadOption`, inode metadata/protobufs, metrics, and Alluxio configuration. It is commonly used as the backing store under `CachingInodeStore`.

## Risks and Edge Cases
- Prefix checking in `RocksIter` must match key encoding exactly; malformed key lengths or default charset assumptions for child names can break listing.
- Iterator clients must close returned iterators to release shared Rocks locks and native iterator resources.
- `hasChildren` checks iterator validity after seeking parent ID; correctness depends on prefix-same-as-start.
- `allInodes` calls `getMutable` while already holding a shared lock, relying on shared-lock reentrancy/ref-count behavior.
- WAL disabled plus batch writes mean crash consistency depends on upstream journal replay.

## Test Signals
Tests should cover key encoding/decoding, prefix/start listing combinations matching heap behavior, missing child edge warning, batch write commit/close, clear/rewrite lock behavior, checkpoint round-trip, iterator close and abort on rewrite, and Rocks metrics registration.
