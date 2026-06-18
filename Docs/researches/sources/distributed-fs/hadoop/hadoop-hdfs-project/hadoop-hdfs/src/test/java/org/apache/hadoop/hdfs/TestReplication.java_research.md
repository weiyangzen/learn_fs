# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplication.java

Purpose: broad replication suite covering rack-aware placement, bad-block reports during transfer, pending replication retry, mismatched replica lengths, corruption handling, late IBRs, and under-construction replication.

Important APIs and types: `MiniDFSCluster`, `DFSClient`, `ClientProtocol`, `LocatedBlocks`, `BlockLocation`, `DatanodeInfo`, `SimulatedFSDataset`, custom `CorruptFileSimulatedFSDataset`, `MaterializedReplica`, `BlockManagerTestUtil`, `InternalDataNodeTestUtils`, `GenericTestUtils.DelayAnswer`, `DataNodeTestUtils`, `MetricsAsserts`, and `AppendTestUtil`.

Control flow: `checkFile` waits for expected replication then verifies block topology paths and rack diversity. `runReplication` creates files with several replication factors on real or simulated storage and checks placement. Bad-block transfer tests use either a simulated dataset that throws on reads or missing/corrupt materialized replicas, then increase replication and assert the destination reports bad blocks and replication does not complete from corrupt sources. Retry tests corrupt/delete replicas on disk, restart with more DNs and short pending timeout, and wait for full replication. Later tests alter replica length, inject corrupt replicas, delay `blockReceivedAndDeleted`, and mark a block corrupt in an under-construction file.

State and persistence behavior: directly manipulates on-disk replicas, DataNode datasets, NameNode corrupt-block metadata, pending reconstruction queues, block reports, IBR timing, and DataNode replication metrics. Some tests persist state across cluster shutdown/restart with `format(false)`.

Dependencies and integration points: integrates rack-aware block placement, DataNode block transfer validation, checksum/corruption reporting, NameNode pending reconstruction, safe-mode thresholds during restart, IBR handling, metrics, and under-construction file behavior.

Risks and edge cases: tests are asynchronous and can time out if block reports or replication work do not schedule promptly. The simulated corrupt dataset throws after successful underlying reads to model transfer failure. Direct replica deletion/corruption is filesystem-layout sensitive. `testNoExtraReplicationWhenBlockReceivedIsLate` guards against over-replication caused by late IBRs by asserting `BlocksReplicated` remains zero.

Test signals: expected replica counts and rack topology, corrupt block flags, successful full replication after retries, truncation detected as corrupt while extension can replicate, no extra replication when IBRs arrive late, and proper replication of non-last blocks in under-construction files.
