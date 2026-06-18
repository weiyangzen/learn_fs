# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetTestUtils.java

Purpose: this private unstable test interface defines white-box operations for manipulating and inspecting DataNode `FsDataset` replicas in tests, abstracting over real and simulated dataset implementations.

Important APIs and types: `ExtendedBlock`, `Replica`, `ReplicaInPipeline`, `ReplicaBeingWritten`, `ReplicaWaitingToBeRecovered`, `ReplicaUnderRecovery`, `FsVolumeSpi`, `Configuration`, `DFSConfigKeys`, `ReflectionUtils`, and `FsDatasetFactory`. The nested `Factory` derives a corresponding `TestUtilsFactory` class from the configured dataset factory class name.

Control flow: `Factory.getFactory` reads `dfs.datanode.fsdataset.factory`, asserts the name contains `Factory`, replaces the suffix with `TestUtilsFactory`, and instantiates it as a `Factory`. Implementations then create utility instances for a DataNode and report default data-dir counts. The interface exposes methods to create replicas in finalized/RBW/pipeline/recovery states, corrupt/truncate/delete block and metadata files via `MaterializedReplica`, inspect stored lengths and generation stamps, change persisted generation stamps, iterate stored replicas, query pending async deletion count, and verify block-pool presence/absence.

State and persistence: this is a contract for persistent dataset mutation. Implementations may write files, corrupt files, delete metadata, or alter generation stamps, and those changes may survive MiniDFSCluster shutdown depending on the underlying dataset.

Dependencies and integration points: many HDFS tests use this abstraction to avoid hard-coding `FsDatasetImpl` layout. It is also the hook that allows `SimulatedFSDataset` to provide compatible behavior where possible.

Risks: reflective factory naming is convention-based and brittle. Methods intentionally permit destructive corruption, so tests must scope blocks and cleanup carefully. Because the interface is marked unstable, implementations and callers must evolve together.

Test signals: no local assertions exist. The interface is validated indirectly by block recovery, corruption, scanner, and dataset tests that use it across dataset implementations.
