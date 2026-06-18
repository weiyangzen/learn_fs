<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java

Purpose: Stress-tests random interleavings of HDFS append, snapshot, and truncate operations against a local filesystem mirror. It is intended to catch NameNode, snapshot, lease, and block recovery regressions where file contents or snapshot views diverge after concurrent mutation.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `FSDataOutputStream`, `dfs.allowSnapshot`, `dfs.createSnapshot`, `dfs.deleteSnapshot`, `dfs.append`, `dfs.truncate`, `TestFileTruncate.checkBlockRecovery`, and `AppendTestUtil.checkFullFile`. The nested `DirWorker`, `FileWorker`, and abstract `Worker` classes drive the test. `Worker.State` tracks `IDLE`, `RUNNING`, `STOPPED`, and `ERROR` with `AtomicReference`, `AtomicBoolean`, and `SubjectInheritingThread`.

Control flow: `startUp` configures a 4-DataNode cluster with small 1 KiB blocks/checksums, short heartbeats, short reconstruction pending timeout, and best-effort datanode replacement. `testAST` creates `/dir`, enables snapshots, initializes a local test directory, starts ten `FileWorker` threads plus one `DirWorker`, runs for 20 seconds, then stops and verifies all files and remaining snapshots. `FileWorker.call` randomly checks full contents, appends random bytes, truncates by arbitrary byte counts, or truncates to block boundaries. `DirWorker.call` randomly pauses all file workers, snapshots the HDFS directory while copying local files to a local snapshot directory, checks existing snapshots, or deletes snapshots.

State and persistence behavior: The test keeps two state stores in sync: HDFS and a local filesystem mirror under `GenericTestUtils.getTestDir`. Snapshot metadata is tracked in `snapshotPaths`, while local snapshot copies model point-in-time contents. Truncate may return not-ready, so the test explicitly waits for HDFS block recovery before comparing bytes. Error state is persisted in each worker's `thrown` field and surfaced during final verification.

Dependencies and integration points: Integrates with the HDFS client write path, NameNode snapshot subsystem, file truncate recovery, local `FileUtil`/Commons IO copying, and test logging through `NameNode.stateChangeLog`. It also depends on random scheduling and HDFS lease/block recovery behavior.

Risks: This is intentionally timing-sensitive and can be flaky if worker pause detection, thread interruption, heartbeat timing, or local file cleanup changes. The local mirror is authoritative for expected bytes, so any non-atomic local/HDFS update ordering bug in the test can masquerade as an HDFS regression. The test is long-running by unit-test standards and has broad integration blast radius.

Test signals: Success means all worker threads stop without `ERROR`, every live HDFS file matches its local mirror, every remaining snapshot path has the same entries and byte contents as its local snapshot copy, and append/truncate recovery completed where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java -->
