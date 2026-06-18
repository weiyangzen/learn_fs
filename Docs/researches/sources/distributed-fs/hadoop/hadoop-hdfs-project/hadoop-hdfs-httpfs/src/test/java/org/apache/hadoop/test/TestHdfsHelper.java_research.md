# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfsHelper.java

## Purpose
JUnit 5 extension helper that provisions HDFS configuration and a per-test HDFS directory for methods annotated with `@TestHdfs`. It can start a shared `MiniDFSCluster` with HttpFS-relevant features enabled.

## Important APIs, Types, And Functions
`TestHdfsHelper` extends `TestDirHelper`. Public accessors are `getMiniDFSCluster()`, `getHdfsTestDir()`, and `getHdfsConf()`. `HdfsStatement.evaluate()` prepares configuration and test path. `startMiniHdfs()` builds the singleton cluster. Constants expose test paths for encryption zone and erasure coding fixtures.

## Control Flow
`beforeEach` runs directory setup first, reflects the current method, and if `@TestHdfs` is present creates an `HdfsStatement` keyed by method name. The statement starts or reuses a mini cluster depending on `test.hadoop.hdfs`, puts the configuration and a reset `/tmp/<test>-<counter>` path into inheritable thread-locals, and returns. `afterEach` clears the HDFS thread-locals after superclass cleanup.

## State, Persistence, And Dependencies
The shared `MINI_DFS` static persists across tests. Per-test state is stored in `InheritableThreadLocal<Configuration>` and `InheritableThreadLocal<Path>`. The mini cluster uses test directories under `TEST_DIR_ROOT`, a JCEKS key provider, ACLs, xattrs, storage policy satisfier mode, WebHDFS regexes, an encryption zone, and an erasure-coded directory/file.

## Integration Points
Integrates Hadoop user test configuration, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `JavaKeyStoreProvider`, WebHDFS client patterns, encryption zone support, and erasure coding policy setup. HttpFS tests consume the returned conf and paths.

## Risks
The singleton cluster creates shared mutable state across tests; only the per-test path is reset. The mini cluster starts many data nodes based on the erasure coding policy, which can be expensive. A failure in encryption or erasure-coding setup blocks all annotated tests. Thread-local state must be removed to avoid cross-test contamination.

## Test Signals
Annotated tests should see non-null HDFS config and paths, writable `/tmp` and `/user`, valid encryption and erasure-coding fixtures, and expected user/ACL regex behavior. Repeated failures often point to MiniDFS startup, key-provider, or cleanup issues.
