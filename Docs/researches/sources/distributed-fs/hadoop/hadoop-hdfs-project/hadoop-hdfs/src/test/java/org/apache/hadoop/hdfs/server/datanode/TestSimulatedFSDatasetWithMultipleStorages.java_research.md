# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDatasetWithMultipleStorages.java

Purpose: This subclass reuses `TestSimulatedFSDataset` with two configured data directories to validate multi-storage behavior in the simulated dataset.

Important APIs/types/functions: `DFS_DATANODE_DATA_DIR_KEY`, `SimulatedFSDataset.getStorageReports`, inherited `pTestSimulatedFSDataset`, and inherited block-report assertions.

Control flow: The constructor sets the inherited expected storage count to two. Setup calls the parent configuration factory setup and then sets the DataNode data-dir key to `data1,data2`. The local test instantiates a simulated dataset and asserts two storage reports; inherited tests now expect two storage block-report entries.

State and persistence behavior: Storage state is in-memory but follows the configured DataNode directory list. No local directories are required because this is simulated storage.

Dependencies and integration points: It checks that common `SimulatedFSDataset` behavior remains correct when the DataNode presents multiple storages, which affects block-report map sizes and storage-report arrays.

Risks and test signals: Signal is the two-entry storage report count plus inherited block-report storage count assertions. Risk is low, but it depends on configuration parsing matching real DataNode storage semantics.
