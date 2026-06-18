# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetImplTestUtilsFactory.java

Purpose: this factory adapts the default `FsDatasetImplTestUtils` implementation to the generic `FsDatasetTestUtils.Factory` contract.

Important APIs and types: `FsDatasetTestUtils.Factory`, `FsDatasetTestUtils`, `FsDatasetImplTestUtils`, and `DataNode`.

Control flow: `newInstance(DataNode datanode)` returns a new `FsDatasetImplTestUtils` bound to the supplied DataNode. `getDefaultNumOfDataDirs()` returns `FsDatasetImplTestUtils.DEFAULT_NUM_OF_DATA_DIRS`.

State and persistence: the factory has no state and performs no persistence. The returned utility operates on a real DataNode dataset and may perform persistent operations, but this class only constructs it.

Dependencies and integration points: it is the default test-utility factory selected by `FsDatasetTestUtils.Factory.getFactory` when the configured dataset factory resolves to the normal `FsDatasetFactory`. It keeps tests generic across real and simulated datasets.

Risks: class-name convention matters: `FsDatasetTestUtils.Factory.getFactory` derives `...TestUtilsFactory` from the configured dataset factory name, so renaming this class or changing package placement would break reflective lookup. The implementation is intentionally small and should remain aligned with `FsDatasetImplTestUtils`.

Test signals: no direct tests live here. Successful dataset white-box tests using the default dataset factory confirm that reflective selection and default data-dir counts still work.
