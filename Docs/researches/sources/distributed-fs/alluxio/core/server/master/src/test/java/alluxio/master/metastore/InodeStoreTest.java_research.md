# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTest.java

Purpose: common inode store contract tests for heap, Rocks, and caching Rocks implementations.

Important APIs/types/functions: extends `InodeStoreTestBase`, using `InodeStore`, `MutableInodeDirectory`, `MutableInodeFile`, `Inode`, `WriteBatch`, `CloseableIterator`, `RocksInodeStore`, `CachingInodeStore`, and Rocks config key `ROCKS_INODE_CONF_FILE`.

Control flow: Rocks-specific tests reopen stores with valid or invalid Rocks options files, expecting successful read/write or a `RocksDBException` cause. CRUD tests cover `get`, `getMutable`, `getChild`, inode removal, child edge removal, and updating inode modification time. `batchWrite` verifies atomic write/remove of inode and edge for stores that support batches. Listing tests add/remove/re-add children, repeatedly remove and add the same edge, force cache churn with extra directories, and check child listing size. `manyOperations` builds a 100-directory deep tree with files, verifies presence, deletes all files and parent edges, then renames a middle directory to root and verifies descendant linkage and old parent emptiness.

State and persistence behavior: heap state is in-memory; Rocks/caching state persists in temporary directories. Inode and edge state are tested together through parent-child lookups and listings.

Dependencies and integration points: captures the core contract consumed by `InodeTree` and file-system master metadata operations.

Risks: locking correctness is delegated to base helper locks but concurrent mutation is not tested here. Batch rollback/failure behavior is not covered.

Test signals: strong cross-implementation signal for inode/edge CRUD, listing consistency, batch writes, and Rocks config handling.
