# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLargeDirectoryDelete.java

**Purpose:** Regression test ensuring recursive deletion of a large directory does not monopolize the NameNode and still allows other client and lock operations to make progress.

**Important APIs and flow:** Static `CONF` uses one-byte HDFS blocks and one-byte checksums so each 100-byte file contributes 100 blocks. `createFiles()` creates files under `/root` with random directory depth until `TOTAL_BLOCKS` reaches 10,000. `getBlockCount()` reads `FSNamesystem.getBlocksTotal()`. `runThreads()` starts two `SubjectInheritingThread` subclasses while deleting `/root`.

**Control flow:** One worker repeatedly creates and deletes small `/tmpN` files while block count is between zero and `TOTAL_BLOCKS`; the other repeatedly acquires and releases the NameNode global write lock and increments `lockOps`. The main thread recursively deletes `/root`, waits for the `BlockManager` marked-delete queue to drain with `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty()`, stops workers, rethrows worker failures, and asserts `lockOps + createOps > 0`.

**State and persistence behavior:** The test mutates a large namespace tree and block map, then verifies deletion processing progresses asynchronously enough for concurrent namespace operations or lock acquisition. It does not restart the cluster; persistence is not the target. The important state is block count, pending deletion queue, and progress counters.

**Dependencies and integration points:** Integrates `MiniDFSCluster`, `DFSTestUtil`, `FSNamesystem` locking with `RwLockMode.GLOBAL`, `BlockManagerTestUtil`, `SubjectInheritingThread`, and recursive `FileSystem.delete()`.

**Risks and test signals:** The random directory shape and concurrent timing can make the exact mix of create and lock operations nondeterministic, so the assertion only requires any progress. Passing signals large recursive deletes yield sufficiently and do not block all NameNode work until every block deletion is processed.
