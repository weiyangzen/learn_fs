# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksStore.java

## Purpose
`RocksStore` manages a RocksDB instance for Alluxio master metastores. It owns database creation, reset, close, checkpoint compression, checkpoint restore, table config helpers, and a custom shared/exclusive lock protocol that protects native RocksDB resources during concurrent reads, writes, checkpoints, clears, restores, and shutdown.

## Important APIs and Types
- Constructor accepts store name, DB path, checkpoint path, DB options, column-family descriptors, and column handle references.
- `getDb`, `clear`, `close`, `writeToCheckpoint`, and `restoreFromCheckpoint` manage lifecycle and persistence.
- `checkAndAcquireSharedLock()` returns `RocksSharedLockHandle`.
- `lockForClosing`, `lockForCheckpoint`, and `lockForRewrite` return exclusive handles with different release semantics.
- `shouldAbort(int)` lets long-running readers abort after close/rewrite requests.
- `mRocksDbStopServing` is an `AtomicStampedReference<Boolean>` carrying stop flag plus DB version.
- `mRefCount` tracks shared lock holders.
- Static `checkSetTableConfig` applies block cache, bloom filter, index, and data-block-index settings.

## Control Flow
Initialization takes a rewrite exclusive lock and calls `resetDb`, which stops any existing DB, formats directories, and opens RocksDB with default plus configured column families. Shared lock acquisition checks the stop flag, increments ref count, then checks the flag again to avoid races with close. Exclusive acquisition sets the stop flag, waits up to the configured timeout for shared refs to drain, optionally resets the ref counter if forced, and returns a handle whose close action resets stop/version according to checkpoint or rewrite semantics. Checkpoint writes create a RocksDB checkpoint directory and compress it as either parallel zip or single tar.gz. Restore stops the DB, replaces/decompresses data, and reopens it.

## State and Persistence
Owns the live RocksDB and Checkpoint objects plus column handles. Persistence is the RocksDB directory and checkpoint streams/directories. Version stamps increment on rewrites/restores/clears but not on checkpoints.

## Dependencies and Integration Points
Used by Rocks-backed inode and block stores. Depends on RocksDB Java APIs, Alluxio configuration, retry utilities, compression utilities, file utilities, and runtime exceptions. The lock protocol is consumed by `RocksSharedLockHandle` and `RocksExclusiveLockHandle`.

## Risks and Edge Cases
- Ref-count correctness is critical to avoiding native crashes during close/restore; test mode enforces strict canaries, production logs and resets.
- Forced exclusive locks can invalidate slow readers; long iterators must call `shouldAbort`.
- Checkpoint paths are deleted/recreated; misconfiguration can destroy unexpected directories if paths are wrong.
- Parallel checkpoint restore writes to a temp path under the first configured temp directory and must clean it on failure.
- `checkSetTableConfig` contains a misspelled local variable but behavior is unaffected.

## Test Signals
Tests should cover shared lock race prevention, exclusive timeout and ref-counter reset, version increments on rewrite but not checkpoint, checkpoint single/parallel formats, restore from directory and stream, column handle close/reopen, config-file and property table options, and abort signaling for iterators.
