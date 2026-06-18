<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java

Purpose: Ensures DataNode balancer bandwidth is initialized from configuration, can be changed dynamically through HDFS admin APIs, and is reported correctly by `dfsadmin -getBalancerBandwidth`.

Important APIs, types, and functions: `DFS_DATANODE_BALANCE_BANDWIDTHPERSEC_KEY`, `DistributedFileSystem.setBalancerBandwidth`, `DataNode.getBalancerBandwidth`, `DFSAdmin`, `ToolRunner.run`, and `GenericTestUtils.waitFor`. `runGetBalancerBandwidthCmd` captures `System.out` to validate CLI output.

Control flow: The test configures the default bandwidth to 1 MiB/s, starts a two-DataNode cluster, verifies both DataNodes have the configured value, and checks the admin command for each DataNode IPC address. It then sets bandwidth to 12 MiB/s and waits until both DataNodes expose the new value. A later call with `0` is expected to leave the current value unchanged. Finally, the CLI accepts `1t` and rejects `1e`.

State and persistence behavior: The bandwidth value is DataNode runtime state. The test does not assert restart persistence; it checks initialization from config and live NameNode-to-DataNode command propagation. CLI output capture is transient process state, restored in a `finally` block.

Dependencies and integration points: Exercises `DistributedFileSystem`, DataNode runtime config update handling, DFSAdmin command parsing, IPC listener address construction, unit parsing, and stdout formatting.

Risks: Timing depends on asynchronous propagation, hence the 60-second wait. The test mutates global `System.out`, so failure to restore it would affect later tests; the helper protects this with `finally`. It also uses a static `Configuration`, making accidental cross-test mutation a possible maintenance hazard.

Test signals: Success means DataNodes expose configured and updated bandwidth values, setting `0` does not overwrite the previous value, `-getBalancerBandwidth` prints the expected bytes-per-second string, and DFSAdmin unit parsing behaves as expected for tera and exa suffix examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java -->
