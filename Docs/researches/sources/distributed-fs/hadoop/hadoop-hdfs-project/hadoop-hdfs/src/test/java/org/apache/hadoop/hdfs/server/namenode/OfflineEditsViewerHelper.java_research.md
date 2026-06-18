<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java

Purpose: helper for offline edits viewer tests that generates an edits file containing broad NameNode operation coverage.

Important APIs/types/functions: `generateEdits()` runs operations and returns the finalized edits path; `startCluster(String)` configures and starts a one-name-dir MiniDFSCluster; `shutdownCluster()` tears it down; private `runOperations()` and `getEditsFilename(CheckpointSignature)` produce and locate the rolled edits segment.

Control flow: `startCluster()` configures name/checkpoint dirs, block size, auth-to-local mapping, delegation token usage, ACLs, and nine DataNodes. `runOperations()` obtains the `DistributedFileSystem`, delegates broad operation generation to `DFSTestUtil.runOperations()`, manually logs rolling-upgrade start/finalize opcodes, then rolls the edit log. `getEditsFilename()` uses the returned checkpoint signature to compute the finalized edits file ending at `curSegmentTxId - 1`.

State and persistence: creates real MiniDFSCluster namespace state and finalized edit logs on local disk under the provided directory. It intentionally limits edits storage to one directory for deterministic lookup.

Dependencies and integration points: integrates MiniDFSCluster, `DFSTestUtil`, `FSImage`, `NNStorage`, storage-directory iteration, delegation-token opcodes, ACL opcodes, and rolling-upgrade edit-log APIs.

Risks and test signals: risks include opcode coverage drifting with `DFSTestUtil.runOperations()` and assumptions about one edits directory. Test signal is an existing finalized edits file that offline viewer tests can parse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java -->
