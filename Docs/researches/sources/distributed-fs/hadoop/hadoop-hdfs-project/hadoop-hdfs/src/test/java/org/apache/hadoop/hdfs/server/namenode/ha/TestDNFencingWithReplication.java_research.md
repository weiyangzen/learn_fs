# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencingWithReplication.java

## Purpose
`TestDNFencingWithReplication` is a slow stress test for HA fencing while replication levels are repeatedly changed during failovers. It targets races between block reconstruction, deletion, block reports, failover proxy retries, and active NameNode changes.

## Important APIs, Types, And Functions
The main test is `testFencingStress`. It uses `HAStressTestHarness` with three NameNodes, one active at a time, short block report and redundancy intervals, and a failover filesystem. The nested `ReplicationToggler` extends `RepeatingTestThread` and alternates a file between replication factor 1 and 2, using `waitForReplicas` to poll block locations until the observed host count matches the requested factor.

## Control Flow
The test creates 20 files at replication 3, starts one toggler per file, adds a harness thread that frequently triggers deletion reports and replication work, and adds a failover thread that changes the active NameNode every five seconds. After the runtime window, it stops all threads and reads every file back through the HA filesystem.

## State And Persistence
The persistent state is the contents and replication metadata of the 20 HDFS files. Transient state includes concurrent client replication changes, NameNode block manager work queues, DataNode block/deletion reports, retry invocation state, and changing active/standby roles across three NameNodes.

## Dependencies And Integration Points
This file integrates `HAStressTestHarness`, `MiniDFSCluster`, `DFSTestUtil`, `FileSystem.setReplication`, `getFileBlockLocations`, `BlockLocation`, `GenericTestUtils.waitFor`, and `MultithreadedTestUtil`. It also suppresses noisy FSNamesystem audit, server, and retry logs for stress execution.

## Risks
The test is intentionally nondeterministic and long-running. Failures may reflect true fencing races, slow replication under local load, or timeouts waiting for block locations. Any change to block placement, redundancy scheduling, heartbeat timing, or failover retry behavior can affect it.

## Test Signals
The primary signals are successful toggler execution without uncaught exceptions, `waitForReplicas` reaching both target replica counts, and every file remaining readable after repeated failovers.
