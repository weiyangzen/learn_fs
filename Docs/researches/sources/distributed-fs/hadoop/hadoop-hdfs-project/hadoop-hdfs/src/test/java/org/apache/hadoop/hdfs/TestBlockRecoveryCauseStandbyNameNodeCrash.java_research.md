<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java

Purpose: Reproduces a high-availability erasure-coded lease recovery scenario where commit block synchronization after deleting/committing an EC block group must not crash the standby NameNode.

Important APIs, types, and functions: `MiniDFSNNTopology.simpleHATopology`, `DistributedFileSystem`, `DFSStripedOutputStream`, `StripedDataStreamer`, `DataNodeTestUtils.pauseIBR/resumeIBR`, `Whitebox.setInternalState`, `GenericTestUtils.waitFor`, `recoverLease`, and `DataStreamer.waitForAckedSeqno`.

Control flow: `setup` configures EC block size, socket timeout, heartbeats, HA edit tailing/log rolling, and a two-NameNode HA cluster with `dataBlocks + parityBlocks` DataNodes. It enables the default EC policy on a test directory. The test pauses incremental block reports on parity-plus-one DataNodes, creates an EC file, writes slightly more than one full EC block group, waits for every striped streamer to ack queued packets, replaces each streamer's `blockStream` with a null output stream to simulate a quiet client failure, and invokes lease recovery as another user. Finally it resumes paused IBRs.

State and persistence behavior: NameNode HA edit state, EC block group metadata, DataNode IBR queues, and client streamer internals are deliberately manipulated. The test is not asserting file content; it asserts recovery and standby edit processing survive this interleaving. `newConf` points clients at the cluster configuration for active NameNode access.

Dependencies and integration points: Deeply integrates EC writing, striped streamers, lease recovery, HA standby tailing, DataNode IBR behavior, fake UGI users, and test-only whitebox mutation of streamer internals.

Risks: This is timing-sensitive and relies on internal field names (`blockStream`) and EC policy defaults. It can become brittle if streamer internals, HA timing, or EC block group accounting changes. The assertion is mostly absence of failure; a standby crash manifests indirectly as an exception or timeout.

Test signals: Success means manual lease recovery completes within the wait window after the simulated client failure and paused IBR condition, with no thrown failure from the active/standby NameNode path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java -->
