# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogJournalFailures.java

## Purpose
`TestEditLogJournalFailures` verifies NameNode behavior when one or more edit journals fail during write, flush, `setReadyToFlush`, or log-segment start. It is parameterized over synchronous and asynchronous edit logging and checks that redundant failures are tolerated up to configured thresholds while required or total failures halt the NameNode.

## Important APIs, Types, And Functions
The suite uses `MiniDFSCluster`, `FSEditLog`, `FSImage`, `JournalSet.JournalAndStream`, `JournalManager`, `EditLogFileOutputStream`, `DistributedFileSystem.rollEdits`, and configuration keys such as `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`, `DFS_NAMENODE_EDITS_DIR_MINIMUM_KEY`, and `DFS_NAMENODE_CHECKED_VOLUMES_MINIMUM_KEY`. Helper methods `invalidateEditsDirAtIndex`, `spyOnStream`, `spyOnJASjournal`, `getJournalAndStream`, and `doAnEdit` inject controlled failures.

## Control Flow
The default setup starts a no-datanode cluster with system exit checking disabled. Tests first perform a mkdir edit, replace selected journal streams with Mockito spies that throw on specific calls, and then perform another edit or roll. Single non-required failures on flush or `setReadyToFlush` should leave the cluster alive. Failure of all journals, a required journal, too many journals below the minimum, or too few successful `startLogSegment` calls should return a `RemoteException` wrapping `ExitException`.

## State And Persistence Behavior
The suite validates the active/inactive status of journal streams and the NameNode's durability threshold decisions. In the required-journal case, it also asserts that after a required journal fails during `setReadyToFlush`, later non-required journals are not asked to set ready, preventing partial side effects from HDFS-2874. The tests do not inspect on-disk log bytes directly; they validate persistence availability through journal state and exception messages about unsynced transactions.

## Dependencies And Integration Points
This class integrates journal quorum/minimum policy, required-edits-dir configuration, NameNode shutdown behavior, RPC exception wrapping, and filesystem mutation. It depends on Mockito spies because actual disk failures would be slower and less deterministic.

## Risks And Test Signals
The main risks are continuing after too little durable edit storage, halting too aggressively when redundancy remains, or partially advancing non-required streams after a required-stream failure. Test signals are successful mkdirs, safe mode remaining false after tolerated failures, exact exception text for fatal paths, inactive journal state, and verification that non-required streams were not invoked.
