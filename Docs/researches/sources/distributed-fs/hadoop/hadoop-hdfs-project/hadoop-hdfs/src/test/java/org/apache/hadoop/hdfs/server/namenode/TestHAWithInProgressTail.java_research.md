# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHAWithInProgressTail.java

**Purpose:** Tests HA failover when standby NameNode tails in-progress edit-log segments from a Quorum Journal Manager and one JournalNode gives empty or slow responses.

**Important APIs and flow:** `startUp()` enables `DFS_HA_TAILEDITS_INPROGRESS_KEY`, shortens `DFS_QJOURNAL_SELECT_INPUT_STREAMS_TIMEOUT_KEY`, enables standby reads with `HAUtil.setAllowStandbyReads()`, and starts `MiniQJMHACluster`. The test keeps references to the DFS cluster, journal cluster, and both NameNodes.

**Control flow:** `testFailoverWithAbnormalJN()` transitions NN0 active, stops NN1's `EditLogTailer`, creates a directory through NN0, transitions NN0 standby, then replaces NN1's edit log with a Mockito spy. The spy intercepts `recoverUnclosedStreams()` and calls `spyOnJASjournal()` to replace the `JournalManager` with a spying `QuorumJournalManager` whose one JournalNode has empty/slow responses. NN1 is transitioned active and must still serve `getFileInfo()` for the directory created by NN0.

**State and persistence behavior:** The state under test is edit-log durability in QJM and the standby's ability to recover and tail unfinalized segments during failover. The filesystem mutation is a single mkdir that must become visible on the new active.

**Dependencies and integration points:** Integrates HA transition APIs, `MiniQJMHACluster`, `MiniJournalCluster`, `QuorumJournalManager`, `JournalSet.JournalAndStream`, `FSEditLog.recoverUnclosedStreams()`, `EditLogTailer`, and `SpyQJournalUtil`.

**Risks and test signals:** The test is sensitive to QJM timing and internal journal-set structure. A pass signals failover catch-up can survive an abnormal JournalNode while reading in-progress segments, preventing metadata loss during active transition.
