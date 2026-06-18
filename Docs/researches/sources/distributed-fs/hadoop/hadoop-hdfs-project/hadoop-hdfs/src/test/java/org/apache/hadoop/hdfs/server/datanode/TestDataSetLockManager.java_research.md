# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataSetLockManager.java

Purpose: unit-tests `DataSetLockManager` hierarchical read/write lock behavior and leak detection for block-pool, volume, and directory lock levels.

Important APIs and types: `DataSetLockManager`, `AutoCloseDataSetLock`, `DataNodeLockManager.LockLevel`, and `SubjectInheritingThread`. Assertions inspect `manager.getLastException()` after `lockLeakCheck`.

Control flow: setup creates a fresh manager. `testBaseFunc` registers locks for BP, volume, and dir, acquires and closes combinations of write/read locks at different levels, runs leak checks after each valid close sequence, then intentionally leaves a write lock open and expects `"lock Leak"`. `testAcquireWriteLockError` starts a subject-inheriting thread that takes a read lock and then attempts a write lock for the same block pool, waits briefly, and verifies leak detection catches the blocked/acquired state. `testLockLeakCheck` directly leaves a block-pool write lock open and asserts the same error.

State and persistence behavior: all state is in-memory lock-manager state: registered lock hierarchy, held locks, and last exception. Integration points are low-level concurrency primitives used by FsDataset code paths such as directory scanning and replica map updates. Risks include thread timing in `testAcquireWriteLockError`, reliance on exact exception message text, and no explicit closure for intentionally leaked locks. Test signals are null last exception for balanced close paths and `"lock Leak"` for held or blocked locks.
