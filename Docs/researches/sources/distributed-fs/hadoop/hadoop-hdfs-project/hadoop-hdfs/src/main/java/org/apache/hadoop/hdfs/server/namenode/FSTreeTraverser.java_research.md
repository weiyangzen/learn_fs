# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSTreeTraverser.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSTreeTraverser.java

Purpose: `FSTreeTraverser` is an abstract NameNode utility for depth-first namespace traversal that processes file inodes in batches. It is designed for long-running namespace walks that must periodically submit work, throttle, and release/reacquire locks without retaining an entire directory stack in memory.

Important APIs and types: the constructor stores an `FSDirectory`, reads the NameNode read-lock reporting threshold, and creates a `Timer`. `traverseDir` starts traversal from a parent directory, start inode id, and start-after cursor. `traverseDirInt` performs one locked iteration step. `readLock` and `readUnlock` acquire/release both `FSNamesystem` and `FSDirectory` read locks. Abstract hooks define subclass policy: `checkPauseForTesting`, `processFileInode`, `shouldSubmitCurrentBatch`, `checkINodeReady`, `submitCurrentBatch`, `throttle`, and `canTraverseDir`. `TraverseInfo` is an extension holder for subclass-specific traversal metadata.

Control flow: `traverseDir` converts the start-after file into a list of path-component cursors from the traversal root to the current point, then repeatedly calls `traverseDirInt` until the cursor is exhausted. `traverseDirInt` asserts the proper locks, validates the start inode, gets children for current state, resumes at `INodeDirectory.nextChild`, processes file inodes, descends into traversable directories by editing the cursor, and submits batches when the subclass threshold is reached. Around batch submission and read-lock overrun, it releases locks, calls subclass hooks, reacquires locks, revalidates the start inode, and resolves the parent path again.

State and persistence behavior: traversal state is transient: the current inode, start-after path components, batch state held by subclasses, and lock timing. The filesystem namespace may change while locks are released, so `resolvePaths` reanchors the cursor and truncates changed lower-level cursors. No persistent state is written here; subclasses may persist or queue batches.

Dependencies and integration points: it integrates with `FSDirectory`, `FSNamesystem` locking, snapshot current-state child lists, `HdfsFileStatus.EMPTY_NAME`, permission-aware path resolution, and `INodeDirectory.nextChild`. Subclasses in HDFS features such as re-encryption or storage policy satisfaction can reuse the safe traversal mechanics.

Risks: correctness depends on subclasses respecting lock assumptions and making `processFileInode` idempotent enough for cursor repositioning. Parent deletion/recreation during an unlocked interval ends the current subtree. The read-lock threshold is used as a wall for yielding, so misconfiguration can either hold locks too long or yield too often. `resolvePaths` assumes intermediate resolved nodes are directories.

Test signals: tests should simulate traversal across files and directories, resume after `startAfter`, batch submission with lock release, namespace mutation while unlocked, deletion of the start inode, non-traversable directories, long read-hold yielding, and subclass pauses/throttling.
