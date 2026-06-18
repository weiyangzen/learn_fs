# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/BackupManagerTest.java

Purpose: unit tests for backup behavior with server-module metastore dependencies, especially Rocks iterator handling.

Important APIs/types/functions: setup/teardown; helpers `createNewBlock`, `createNewFile`, `createRootDir`; tests `rocksBlockStoreIteratorClosed` and `rocksInodeStoreIteratorNotUsed`.

Control flow: setup creates a master registry, manual clock, and executor. The block-store test mocks `RocksBlockMetaStore.getCloseableIterator` to return a close-tracking iterator, starts metrics and block masters, runs `BackupManager.backup`, and asserts the iterator closed. The inode-store test mocks `RocksInodeStore` so global iterator throws but root `getChildren` works, starts block and filesystem masters, runs backup, and expects no exception.

State and persistence: writes backup output to temporary files and constructs real master registry state with mocked stores. No permanent repo artifacts.

Dependencies/integration: exercises `BackupManager`, `DefaultBlockMaster`, `DefaultFileSystemMaster`, heap and Rocks metastore interfaces, `MetricsMasterFactory`, and `MasterTestUtils`.

Risks: tests depend on backup traversal strategy. The inode test ensures backup walks the inode tree through child iteration instead of using unsupported full Rocks inode iteration.

Test signals: protects resource closure for block iterators and avoids using a disallowed Rocks inode iterator during backup.
