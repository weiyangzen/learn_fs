# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksBlockMetaStoreTest.java

Purpose: tests Rocks-backed block metastore iterator lock cleanup and behavior during checkpoint/restore while long-running readers exist.

Important APIs/types/functions: uses `RocksBlockMetaStore`, `RocksStoreTestUtils.waitForReaders`, `BlockMetaStore.Block`, `CloseableIterator`, `CheckpointInputStream`, `Block.BlockMeta`, executor services, latches, queues, and `PropertyKey.MASTER_METASTORE_ROCKS_EXCLUSIVE_LOCK_TIMEOUT`.

Control flow: setup configures short Rocks exclusive-lock timeouts and test mode, creates a store and executor. `escapingIteratorExceptionInNext` and `escapingIteratorExceptionInHasNext` wrap the store iterator in `FlakyRocksBlockStore`, throw after five iterations from `next` or `hasNext`, and assert shared lock count returns to zero after the exception and close. `longRunningIterAndCheckpoint` disables test mode, prepares 400 blocks, starts 20 iterators that pause after ten entries, writes a checkpoint while readers are paused, releases them, and expects every reader to complete all 400 entries without errors. `longRunningIterAndRestore` writes a checkpoint, pauses 20 readers, restores from the checkpoint while readers are active, releases them, and expects all readers to abort at ten entries with errors because Rocks contents changed.

State and persistence behavior: RocksDB column-family state stores block metadata. Checkpoint writes a non-empty file; restore replaces store contents and invalidates active readers.

Dependencies and integration points: covers Rocks shared/exclusive lock coordination, iterator resource management, block checkpoint/restore, and reader behavior under concurrent maintenance operations.

Risks: timing depends on latches but still uses concurrent threads. The flaky wrapper extends `RocksInodeStore` only to host the wrapper class, so it is test scaffolding rather than a real delegate type.

Test signals: strong signal for avoiding Rocks shared-lock leaks and preserving/aborting long-running iterators appropriately around checkpoint and restore.
