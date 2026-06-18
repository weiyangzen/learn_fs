# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTest.java

## Purpose
`RocksStoreTest` validates the lower-level `RocksStore` wrapper around RocksDB. It covers backup and restore, shared-lock reference counting, exclusive-lock modes for closing, checkpointing, and rewriting, and precedence rules when multiple exclusive operations overlap.

## Important APIs, Types, and Functions
The suite constructs `RocksStore` with explicit `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, and an `AtomicReference<ColumnFamilyHandle>`. It exercises `checkAndAcquireSharedLock`, `lockForClosing`, `lockForCheckpoint`, `lockForRewrite`, `writeToCheckpoint`, `restoreFromCheckpoint`, `getDb`, `close`, `getSharedLockCount`, `isServiceStopping`, and `shouldAbort`. It asserts error semantics through `UnavailableRuntimeException` and `ExceptionMessage.ROCKS_DB_CLOSING` or `ROCKS_DB_REWRITTEN`.

## Control Flow, State, and Persistence
`setup` creates temporary Rocks and backup directories, initializes a single column family with a fixed-length long prefix extractor, and opens a test store. `backupRestore` writes keys into RocksDB under a shared lock, serializes a checkpoint, closes the store under a closing lock, opens a new store, restores under a rewrite lock, and verifies the keys. Lock tests acquire long-lived shared locks in executor tasks, then attempt exclusive operations with `TEST_MODE` either enabled to reject forced takeover or disabled to permit it. Exclusive-operation ordering tests assert that close has higher priority than checkpoint/rewrite and that checkpoint blocks rewrite.

## Dependencies and Integration Points
This test directly integrates with RocksDB Java objects (`RocksDB`, `WriteOptions`, `RocksObject`, `ColumnFamilyHandle`) and Alluxio metastore lock handles (`RocksSharedLockHandle`, `RocksExclusiveLockHandle`). It relies on Alluxio configuration keys for timeout and test mode and on checkpoint streams for restore.

## Risks
The suite deliberately manipulates global `Configuration` and forced-lock behavior, so isolation matters. Concurrent tests rely on latch ordering and a short lock timeout, making them sensitive to slow or overloaded CI environments. `tearDown` closes Rocks objects in reverse order, but earlier assertion failures inside lock scenarios can still leave resources to be closed by the teardown path.

## Test Signals
Passing tests show that reference counts do not go negative or leak after forced exclusive locks, readers may continue after checkpoint but not after rewrite, closing state is sticky, and backup/restore preserves column-family data. Any failures in these tests should be treated as high-risk for master metastore durability or shutdown behavior.
