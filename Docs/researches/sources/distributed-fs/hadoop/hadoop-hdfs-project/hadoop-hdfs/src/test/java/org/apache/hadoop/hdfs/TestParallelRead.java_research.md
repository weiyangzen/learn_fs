# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelRead.java

## Purpose
This subclass runs the shared `TestParallelReadUtil` workload over the normal TCP HDFS read path. It is also a regression guard that configured domain socket paths are ignored when both short-circuit local reads and UNIX-domain data traffic are disabled.

## Important APIs, Types, And Functions
`setupCluster` creates an `HdfsConfiguration`, sets `HdfsClientConfigKeys.Read.ShortCircuit.KEY` false, sets `DFS_CLIENT_DOMAIN_SOCKET_DATA_TRAFFIC` false, gives `DFS_DOMAIN_SOCKET_PATH_KEY` a path that should not be created, and delegates to `TestParallelReadUtil.setupCluster`. `teardownCluster` delegates to the base utility.

## Control Flow
JUnit `@BeforeAll` prepares one shared `BlockReaderTestUtil` cluster with default replication. The inherited tests then create files, start multiple `ReadWorker` threads, and exercise copying, direct `ByteBuffer`, mixed, and no-checksum read workloads. `@AfterAll` shuts down the utility cluster.

## State And Persistence
State is inherited from `TestParallelReadUtil`: static cluster utility, `DFSClient`, random seed, file data, open `DFSInputStream`s, and checksum verification flag. This subclass contributes transport configuration state only and has no restart persistence concerns.

## Dependencies And Integration Points
It integrates the HDFS TCP block reader path, `DFSInputStream`, client read configuration, and the base parallel-read workload.

## Risks
Because the subclass has no test methods of its own, any lifecycle failure prevents inherited tests from running. The bogus domain socket path intentionally verifies ignored configuration; if future code validates it unconditionally this test should fail.

## Test Signals
Signals are all inherited parallel-read checks passing while short-circuit and domain socket paths are disabled, plus absence of attempts to create or bind the configured impossible socket path.
