# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeInitStorage.java

## Purpose

`TestDataNodeInitStorage` verifies DataNode startup ordering: the DataNode UUID must be initialized in `DataStorage` before the configured FsDataset factory constructs the dataset.

## Important APIs, Types, and Functions

The nested `SimulatedFsDatasetVerifier` extends `SimulatedFSDataset`. Its nested `Factory` extends `FsDatasetSpi.Factory<SimulatedFSDataset>` and constructs `SimulatedFsDatasetVerifier`. `setFactory` writes `DFS_DATANODE_FSDATASET_FACTORY_KEY` into configuration. The verifier constructor logs and asserts `storage.getDatanodeUuid()` is non-null and non-empty.

## Control Flow

The test builds `HdfsConfiguration`, installs the custom dataset factory, starts a one-DataNode MiniDFSCluster, waits for active, and shuts it down. Dataset construction is the assertion point: if DataNode UUID assignment has not happened before FsDataset initialization, the constructor assertion fails during cluster startup.

## State and Persistence Behavior

The test observes DataNode storage identity state, specifically the in-memory `DataStorage` UUID loaded or created during startup. The MiniDFSCluster owns temporary storage directories, but the test does not inspect files directly.

## Dependencies and Integration Points

It integrates DataNode storage initialization, the pluggable FsDataset factory key, `FsDatasetSpi.Factory`, and MiniDFSCluster startup. It is a regression test for startup sequencing between `DataStorage` and dataset construction.

## Risks and Edge Cases

The assertions use Java `assert`, which only fires when assertions are enabled in the test JVM. The test only covers simulated dataset factory construction and does not verify UUID persistence across restarts. A startup refactor could bypass the custom factory or change constructor timing.

## Test Signals

The cluster reaches `waitActive()` without assertion failure. The meaningful signal is the constructor assertion that `storage.getDatanodeUuid()` exists before `SimulatedFSDataset` initialization finishes.
