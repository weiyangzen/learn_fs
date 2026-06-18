# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRenameWhileOpen.java

Purpose: verifies HDFS edit-log and fsimage persistence for files that remain open while their parent directory or file path is renamed, including restart and lease recovery scenarios.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream`, `FSEditLog`, Mockito `spy`, `DFSTestUtil.setEditLogForTesting`, `TestFileCreation`, `DFS_NAMENODE_HEARTBEAT_RECHECK_INTERVAL_KEY`, `DFS_HEARTBEAT_INTERVAL_KEY`, and `DFS_NAMENODE_SAFEMODE_THRESHOLD_PCT_KEY`.

Control flow: each test creates one or more open files, hflushes them, performs a rename while the stream remains open, shuts down and restarts the cluster without formatting once or twice, then verifies old paths are gone and new paths exist. `testWhileOpenRenameParent` also spies the edit log so `endCurrentLogSegment` is not called, creates and renames another file with a pending add-block operation, stops the NameNode before closing, and validates edit-log replay.

State and persistence behavior: exercises lease persistence in fsimage and edit logs, rename records for open files, pending add-block edit replay, and path reconstruction across NameNode restarts. Streams are intentionally not closed before shutdown to keep leases active.

Dependencies and integration points: integrates file creation helpers, NameNode edit log, lease manager, rename semantics, fsimage reload, edit replay, and MiniDFSCluster restart with `format(false)`.

Risks and edge cases: `checkFullFile` is currently a no-op because lease recovery validation is commented, so path existence is the primary signal. The tests use sleeps for IPC idle and restart timing. The first test modifies the NameNode edit log through a spy, a brittle but targeted way to force replay coverage.

Test signals: old open-file paths no longer exist, renamed paths exist after restart(s), independent file paths still exist, and cluster reload succeeds with active leases and pending add-block edits.
