# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteBlockGetsBlockLengthHint.java

Purpose: Regression test ensuring DFSClient propagates the intended block length hint through the DataTransferProtocol path to the DataNode dataset layer when creating RBW replicas.

Important APIs and types: `DFSTestUtil.createFile`, `SimulatedFSDataset`, `FsDatasetSpi.Factory`, `DataNode`, `DataStorage`, `ExtendedBlock`, `ReplicaHandler`, `StorageType`, and overridden `createRbw`.

Control flow: `blockLengthHintIsPropagated` installs custom `FsDatasetChecker` as the datanode dataset factory, sets default block length to 1024, disables volume scanner, starts one datanode, and creates a file with expected block length 2048. `FsDatasetChecker.createRbw` asserts the local block byte count equals `EXPECTED_BLOCK_LENGTH` before delegating to `SimulatedFSDataset`.

State and persistence behavior: The custom simulated dataset sees block creation state only during test execution. Assertion failure occurs at RBW creation time, before normal file completion can hide the incorrect hint.

Dependencies and integration points: Integrates DFSOutputStream, BlockReceiver/DataTransferProtocol, DataNode FsDataset factory configuration, simulated storage, and block metadata.

Risks and test signals: The test relies on the dataset override being used by the MiniDFSCluster and on `createFile` exercising RBW creation. Passing signals the block-length hint survives client-to-datanode plumbing.
