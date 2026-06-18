# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithMissingBlocks.java

Purpose: verifies striped-file reads when the NameNode returns block locations with some internal blocks missing because the corresponding DataNodes are down.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `BlockLocation`, `DatanodeInfo`, `ErasureCodingPolicy`, `DatanodeReportType.DEAD`, `StripedFileTestUtil.verifySeek`, `verifyStatefulRead`, `verifyPread`, and `DFSTestUtil.writeFile`.

Control flow: setup configures EC block size, disables replication max streams, starts `data + parity + 2` DNs, enables default EC policy, and creates a separate `DFSClient`. The test writes one striped file, waits for reports, verifies length, then iterates missing data counts and parity counts within decode tolerance. `readFileWithMissingBlocks` captures initial block locations, stops selected DNs by matching xfer ports in the first block location, asserts the new location list shrank, runs seek/stateful/pread verification, then restarts all dead DNs.

State and persistence behavior: deliberately changes cluster liveness and NameNode block location output without deleting file metadata. Restarting dead DNs and triggering heartbeats resets the cluster before the next combination.

Dependencies and integration points: integrates filesystem block-location API, DataNode liveness tracking, dead-node reports, client striped seek/read/pread implementations, and default EC policy geometry.

Risks and edge cases: `missingData` loop ranges up to the number of data blocks, while `missingParity` is bounded by parity minus missing data; this models recoverable missing sets. The DataNode stop routine relies on `BlockLocation.getNames()` order and port matching. The test uses a single file repeatedly and must restore DNs after each case.

Test signals: reduced block-location count after DN shutdown, successful seek/stateful/pread content verification, and dead DataNodes restarting cleanly.
