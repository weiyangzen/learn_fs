# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetTimes.java

Purpose: Tests HDFS file and directory access-time/modification-time behavior, including explicit `setTimes`, close-time mtime updates, access-time lock behavior, disabled automatic atime support, and persistence after NameNode restart.

Important APIs and types: `FileSystem.setTimes`, `FileStatus.getAccessTime`, `FileStatus.getModificationTime`, `FSDataOutputStream.close`, `DFSClient.datanodeReport`, `NameNodeAdapterMockitoUtil.spyOnFsLock`, `MockitoUtil.doThrowWhenCallStackMatches`, `DFS_NAMENODE_ACCESSTIME_PRECISION_KEY`, and `MiniDFSCluster`.

Control flow: `writeFile` writes deterministic data. `testTimes` creates a file, records atime/mtime before and after close, verifies `-2` leaves times unchanged, sets atime and mtime independently, sets directory times, validates a missing path error, restarts the cluster without formatting, and checks persisted times. `testTimesAtClose` confirms mtime changes when a written file is closed. `testGetBlockLocationsOnlyUsesReadLock` spies on the FSNamesystem lock and fails if `getBlockLocations` takes the write lock when atime precision says no update is needed. `testAtimeUpdate` disables automatic atime updates but verifies explicit `setTimes` still sets atime.

State and persistence behavior: HDFS metadata times are stored in NameNode namespace/edit log state and are verified across restart in `testTimes`. DataNode reports are only diagnostic on failure.

Dependencies and integration points: Integrates `FileSystem`, `DFSClient`, NameNode locking, heartbeat timing, datanode reports, Mockito-based lock spying, and HDFS access-time precision configuration.

Risks and test signals: Timing comparisons can be sensitive to clock granularity and restart timing. Passing signals that time metadata updates are durable, close updates mtime, explicit atime works even when automatic atime is disabled, and read-only block-location paths avoid unnecessary write locking.
