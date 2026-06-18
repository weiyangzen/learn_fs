# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreTestBase.java

Purpose: shared parameterization and helper layer for inode store tests.

Important APIs/types/functions: provides parameter suppliers for `HeapInodeStore`, `RocksInodeStore`, and `CachingInodeStore`; configures cache size, eviction batch size, and Netty leak detector settings; owns `InodeLockManager`, root inode, and helper methods `writeInode`, `writeEdge`, `removeInode`, `removeParentEdge`, `inodeDir`, and `inodeFile`.

Control flow: static `parameters` creates a temporary directory and writes a Rocks options file used by child tests. `before` creates a new lock manager and store for each parameter. `after` closes the store. Helper methods acquire write locks for inode or edge operations before delegating to the store.

State and persistence behavior: test stores are fresh per test method but may share a static base directory. Lock acquisition models production expectations around inode/edge mutation.

Dependencies and integration points: all derived inode store tests rely on this to run identical scenarios against heap, Rocks, and caching implementations. The Rocks config string defines default, inodes, and edges column-family options.

Risks: static directory reuse means Rocks-backed tests must close/clear correctly to avoid cross-test contamination. Helpers hide lock boilerplate, so tests may not catch callers that omit locks unless the implementation enforces them.

Test signals: foundational infrastructure, not standalone coverage; it ensures derived tests exercise the same contract across implementations under leak-detection settings.
