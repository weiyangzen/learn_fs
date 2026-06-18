<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java

Purpose: command-line benchmark harness that measures NameNode throughput for namespace and block-management operations by calling NameNode protocols directly, with either an embedded NameNode or a remote HDFS URI.

Important APIs/types/functions: top-level implements `Tool`. `OperationStatsBase` owns common argument parsing, thread scheduling, timing, cleanup, safe-mode/save behavior, and stats aggregation. `StatsDaemon` runs per-thread operations. Concrete operations are `CleanAllStats`, `CreateFileStats`, `MkdirsStats`, `OpenFileStats`, `DeleteFileStats`, `AppendFileStats`, `FileStatusStats`, `RenameFileStats`, `BlockReportStats`, and `ReplicationStats`. `TinyDatanode` simulates DataNode registration, heartbeats, block reports, and block-received reports.

Control flow: `run()` parses `-op`, builds one or more operation objects, starts an embedded NameNode when no HDFS URI is configured, initializes protocol handles and block-pool ID, then benchmarks and cleans each operation before printing stats. Each operation pre-generates inputs, launches `StatsDaemon` threads, busy-waits until they finish, and aggregates local counts/timing. Namespace operations create generated paths and call `ClientProtocol`; block-report and replication benchmarks register simulated DataNodes, create files/blocks, submit reports, decommission nodes, and force block-manager work computation.

State and persistence: benchmark state includes generated test paths under `/nnThroughputBenchmark`, static protocol handles, include/exclude host files under `hadoop.tmp.dir`, simulated DataNode block lists, and NameNode namespace/edit-log state. `-keepResults` preserves benchmark namespace and may save a checkpoint; default cleanup deletes the base dir.

Dependencies and integration points: depends on NameNode client, datanode, namenode, and refresh-user-mapping protocols, `DFSTestUtil`, `FileNameGenerator`, `BlockManagerTestUtil`, `DatanodeProtocolClientSideTranslatorPB`, and Hadoop `ToolRunner`/generic options.

Risks and test signals: risks include static global protocol state, busy-waiting, direct protocol calls that bypass client behavior, remote replication benchmark limitations, and simulated DataNodes that only model selected DataNode behavior. Test signals are benchmark logs showing inputs, operations executed, elapsed time, average latency, ops/sec, block distribution, decommissioned blocks, and pending replications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java -->
