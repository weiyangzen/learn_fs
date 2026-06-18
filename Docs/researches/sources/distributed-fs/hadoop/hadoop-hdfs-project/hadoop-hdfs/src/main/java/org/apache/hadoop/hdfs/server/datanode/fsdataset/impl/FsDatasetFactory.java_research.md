# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetFactory.java

Purpose: concrete factory that wires the `FsDatasetSpi.Factory` extension point to the default local-disk `FsDatasetImpl`.

Important APIs/types/functions: `newInstance(DataNode datanode, DataStorage storage, Configuration conf)` constructs and returns `new FsDatasetImpl(datanode, storage, conf)`.

Control flow: `FsDatasetSpi.Factory.getFactory(conf)` selects this class by default unless configuration overrides `DFS_DATANODE_FSDATASET_FACTORY_KEY`. DataNode startup calls `newInstance` to build its dataset.

State and persistence: this factory has no state. Persistence is delegated entirely to the constructed `FsDatasetImpl`.

Dependencies and integration points: depends on `Configuration`, `DataNode`, `DataStorage`, `FsDatasetSpi.Factory`, and `FsDatasetImpl`. It is the default bridge between configuration and local dataset implementation.

Risks: constructor exceptions propagate as `IOException` and can fail DataNode startup. Any custom factory must remain compatible with the same SPI expectations. This class does not override `isSimulated`, so it reports non-simulated through the base implementation.

Test signals: default factory selection, successful `FsDatasetImpl` construction with test DataNode/storage, override behavior through configuration, and startup failure propagation.
