# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreCheckpointTest.java

Purpose: parameterized checkpoint/restore tests for inode stores across heap, Rocks with default cache, and Rocks with disabled cache.

Important APIs/types/functions: uses `MasterUtils.getInodeStoreFactory`, `MetastoreType`, `InodeStore.writeToCheckpoint`, `restoreFromCheckpoint`, directory checkpoint APIs with an `ExecutorService`, `CheckpointInputStream`, and `InodeLockManager`.

Control flow: parameters cover heap and Rocks variants. Setup configures metastore type/cache size, creates a base store, writes root plus three child directories, and removes inode 2. `testOutputStream` writes a checkpoint to a file output stream, creates a new store, and restores from a checkpoint input stream. `testDirectory` writes and restores a directory-format checkpoint using a two-thread executor. The `@After` method acts as the shared assertion block, verifying restored root, inode 1, missing inode 2, and inode 3, then closing both stores.

State and persistence behavior: checkpoint output is either a single file or a directory. New store state must exactly reflect persisted inode entries and removals.

Dependencies and integration points: covers checkpoint compatibility for metastore factory output and both stream and directory checkpoint protocols.

Risks: assertions run in `@After`, which can obscure failures if setup fails before `mNewInodeStore` is initialized. Edges/children are not explicitly checked, only inode records.

Test signals: solid signal for basic inode checkpoint round-trip across configured metastore implementations.
