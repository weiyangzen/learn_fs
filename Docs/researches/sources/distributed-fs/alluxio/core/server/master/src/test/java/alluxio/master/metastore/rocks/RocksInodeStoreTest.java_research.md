# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksInodeStoreTest.java

## Purpose
`RocksInodeStoreTest` is a JUnit test suite for `RocksInodeStore`, focused on inode persistence, batch writes, iterator formatting, and concurrent interaction between read paths and destructive or exclusive operations such as close, checkpoint, restore, and clear. It is especially concerned with RocksDB shared/exclusive lock correctness and reader behavior when the underlying store generation changes.

## Important APIs, Types, and Functions
The suite exercises `RocksInodeStore.createWriteBatch`, `writeInode`, `addChild`, `get`, `getMutable`, `getChildIds`, `getCloseableIterator`, `writeToCheckpoint`, `restoreFromCheckpoint`, `clear`, and `close`. Test helpers include `submitListingJob`, `submitIterJob`, `submitGetInodeJob`, `submitAddInodeJob`, and the scenario helpers `testConcurrentReaderAndClose`, `testConcurrentReaderAndCheckpoint`, `testConcurrentReaderAndRestore`, and `testConcurrentReaderAndClear`. The nested `FlakyRocksInodeStore` wraps a delegate iterator and throws from `hasNext` or `next` to validate lock cleanup on iterator exceptions. `QuadFunction` lets the same concurrency harness run against list, get, and add workloads.

## Control Flow, State, and Persistence
`setUp` enables Alluxio test mode, configures the Rocks exclusive-lock timeout, creates a temporary Rocks store, and starts a cached executor. Most concurrency tests first call `prepareFiles` to create 400 directory inodes under parent 0, then start 20 reader/writer tasks. Latches stop tasks mid-stream, an exclusive store operation runs, and the tasks are released so the test can assert either completion, empty reads, or abort behavior. Checkpoint tests persist the database into a temp file through `writeToCheckpoint`; restore tests replay that file through `CheckpointInputStream`. Persistent state is limited to temporary RocksDB directories and checkpoint files.

## Dependencies and Integration Points
The file integrates the inode metastore with `MutableInodeDirectory`, `CreateDirectoryContext`, `ReadOption`, Alluxio configuration keys, checkpoint streams, and `CloseableIterator`. It also depends on `RocksStoreTestUtils.waitForReaders` to join asynchronous readers and on JUnit `TemporaryFolder` for isolated Rocks state.

## Risks
The tests are timing sensitive because they depend on 20 worker threads reaching a latch point before an exclusive operation. Test mode is deliberately disabled in long-running iterator cases so forced exclusive-lock behavior can be exercised; forgetting to restore global configuration in nearby tests can affect later suites. The list-reader abort expectations intentionally allow either completed readers or errors depending on scheduling. The `FlakyRocksInodeStore` creates an unused superclass Rocks store path, so resource lifetime must be watched if expanded.

## Test Signals
Useful signals are the full `RocksInodeStoreTest` suite, especially `longRunningIterAndRestore`, `longRunningIterAndCheckpoint`, and the `concurrent*` matrix. Passing tests indicate that shared lock counts return to zero, iterator exceptions close resources, checkpoints are non-empty, restore invalidates stale iterators, and the store remains usable after checkpoint/restore/clear scenarios.
