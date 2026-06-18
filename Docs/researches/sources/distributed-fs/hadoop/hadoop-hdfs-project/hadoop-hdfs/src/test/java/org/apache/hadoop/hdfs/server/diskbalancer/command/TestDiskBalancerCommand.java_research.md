# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/command/TestDiskBalancerCommand.java

## Purpose
`TestDiskBalancerCommand` is an integration and command-line regression test suite for the HDFS `DiskBalancerCLI`. It verifies report, plan, execute, query, cancel, help, and host-file driven reporting behavior against both a deterministic JSON cluster fixture and live `MiniDFSCluster` instances.

## Important APIs, Types, and Functions
- `TestDiskBalancerCommand` owns a shared `MiniDFSCluster`, a `clusterJson` URI pointing at `/diskBalancer/data-cluster-64node-3disk.json`, and an `HdfsConfiguration` with `DFS_DISK_BALANCER_ENABLED` enabled.
- `setUp()` starts a 3-DataNode cluster with 2 storages per DataNode and loads the JSON fixture URI; `tearDown()` explicitly shuts down each `DataNode` and then the cluster.
- `runCommandInternal(...)` tokenizes a shell-like command string with `StringUtils.split`, runs `DiskBalancerCLI` through `ToolRunner`, captures its `PrintStream` output, and returns output lines.
- `runCommand(...)` variants set `FileSystem.setDefaultUri` either to the JSON fixture URI or a live cluster URI before delegating to the CLI runner.
- `runAndVerifyPlan(...)` runs `-plan <datanodeUuid>`, asserts the two-line output contract, and returns the generated full plan path.
- Report helpers exercise `ReportCommand.getNodes` and validate output for node lists, invalid nodes, empty node lists, and `file://` include files.

## Control Flow and Behavior
The suite starts from a default live cluster but many tests create additional short-lived imbalanced clusters with `DiskBalancerTestUtil.newImbalancedCluster`. Plan/execute tests generate a plan, then run `hdfs diskbalancer -execute <plan>`, checking normal success, date-validity failures, `-skipDateCheck` override, and rejection when a DataNode starts with a non-regular `StartupOption.ROLLBACK` state. Report tests default to the JSON fixture so expected output is stable: no top limit, smaller/larger top limits, non-numeric top values, explicit node detail, generic `-fs file:<json>` handling, and output line contents including volume paths, storage types, utilization, and density.

Other tests cover CLI validation paths: invalid extra arguments throw `HadoopIllegalArgumentException`; `-plan` and `-report` together throw `IllegalArgumentException`; cancel with a malformed node target throws; query by UUID can route to `UnknownHostException`; query by `localhost:<ipcPort>` works before a plan has been submitted; help runs without failure. The later report tests validate multiple nodes and node parsing from a host include file with comment handling.

## State and Persistence
The tests deliberately mutate global and process-local state: `FileSystem.setDefaultUri` is changed before CLI invocation, clusters are started and torn down, and plan files are written to local or HDFS-derived paths. Plan validity tests depend on wall-clock plan timestamps and `DFS_DISK_BALANCER_PLAN_VALID_INTERVAL`; `testDiskBalancerExecuteOptionPlanValidity` sleeps for 10 seconds to keep a 600s plan valid. Host-file tests write a temporary include file under `GenericTestUtils.getTestDir()` and delete it afterward. Persistent DiskBalancer plan files are not inspected deeply, but their generated full path is treated as part of the CLI contract.

## Dependencies and Integration Points
This class integrates `DiskBalancerCLI`, `ReportCommand`, `ConnectorFactory`, `DiskBalancerCluster`, `DiskBalancerDataNode`, `MiniDFSCluster`, `DiskBalancerTestUtil`, HDFS configuration keys, and Hadoop `ToolRunner`. The JSON fixture is critical for deterministic report output. Live cluster tests depend on DataNode IPC ports and volume directories from `MiniDFSCluster`.

## Risks and Edge Cases
- Output assertions are line-index sensitive and can fail after benign formatting or ordering changes in the CLI.
- Command strings are split by spaces without shell quoting semantics; paths with spaces would not be represented accurately.
- Tests that sleep or wait on cluster state can be timing-sensitive on slow CI.
- `FileSystem.setDefaultUri` uses shared `Configuration` state; test isolation relies on fresh setup and per-test cluster cleanup.
- Host-file tests manually close `FileWriter`; failures before close or delete can leave local files behind.

## Test Signals
The file itself is a JUnit 5 test suite. Strong signals include successful CLI exit through `ToolRunner`, expected exception types and messages via `assertThrows`/`LambdaTestUtils.intercept`, precise report line content, `ConnectorFactory` JSON parsing yielding 64 nodes, and generated plan output containing the target DataNode UUID.
