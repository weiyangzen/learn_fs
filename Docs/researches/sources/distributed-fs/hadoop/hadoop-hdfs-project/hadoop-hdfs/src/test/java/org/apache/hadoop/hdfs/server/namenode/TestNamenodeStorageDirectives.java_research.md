# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeStorageDirectives.java

Purpose: Ensures storage type and storage ID directives chosen by the NameNode are honored by DFSClient/DataNode writes across HDFS storage policies.

Important APIs and types: Cluster setup configures storage types, storage counts, `VolumeChoosingPolicy`, and `BlockPlacementPolicy`. `verifyFileReplicasOnStorageType` uses `DFSClient.getLocatedBlocks` to inspect `LocatedBlock.getStorageTypes`. `TestVolumeChoosingPolicy` asserts the storage ID passed into volume choice, and `TestBlockPlacementPolicy` returns a controlled `DatanodeStorageInfo`.

Control flow: `testTargetStorageTypes` runs multiple cluster layouts and root storage policies, creates a replicated test file, then verifies expected storage types appear and unexpected types do not. Policies covered include `ONE_SSD`, `ALL_SSD`, `HOT`, `WARM`, `COLD`, `LAZY_PERSIST`, and `ALL_NVDIMM`. `testStorageIDBlockPlacementSpecific` installs custom block placement and volume choosing policies, forces placement to one specific storage, and verifies the same storage ID reaches volume selection during file creation.

State and persistence behavior: Created files persist blocks on storage volumes with specific storage types. Datanode storage state is runtime MiniDFSCluster state, and block location metadata exposes storage types and ids.

Dependencies and integration points: Uses MiniDFSCluster federation topology, DFSClient, block placement, datanode volume choosing, storage policy names, `StorageType`, heartbeat/disk interval tuning, and DataNode failure tolerance configuration.

Risks: Tests can be sensitive to block placement availability when requested storage types are scarce. Custom static fields in nested policy classes must be set before file creation. The verification counts storage type appearances rather than exact complete layout.

Test signals: Passing means block locations contain policy-appropriate storage types, exclude disallowed types, and the storage ID selected by NameNode placement is passed through to DataNode volume selection.
