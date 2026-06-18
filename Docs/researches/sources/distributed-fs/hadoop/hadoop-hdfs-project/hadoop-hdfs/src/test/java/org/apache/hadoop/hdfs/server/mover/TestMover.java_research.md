# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestMover.java

## Purpose
`TestMover` is a slow integration test suite for the HDFS Mover, the tool that migrates block replicas between storage types so files satisfy their storage policies. It covers core scheduling, locality metrics, federation and HA CLI path parsing, erasure-coded striped files, maintenance states, secure keytab execution, pinned block behavior, retry exit codes, unset policies, and mover metrics.

## Important APIs, Types, and Functions
- `initConf(Configuration)` standardizes small block sizes, fast heartbeats/redundancy checks, moved-window timing, and disables internal Storage Policy Satisfier by setting `StoragePolicySatisfierMode.NONE`.
- `newMover(Configuration)` builds a single `NameNodeConnector` from `DFSUtil.getInternalNsRpcUris` and constructs a `Mover`.
- `testMovementWithLocalityOption(...)` creates local or cross-node storage layouts, changes a directory policy from HOT to COLD, runs `Mover.Cli`, waits for ARCHIVE locations, and checks DataNode replace-block locality counters.
- `setupStoragePoliciesAndPaths(...)`, `waitForLocatedBlockWithDiskStorageType(...)`, and `waitForLocatedBlockWithArchiveStorageType(...)` are shared federation and movement helpers.
- CLI tests call `Mover.Cli.getNameNodePathsToMove(...)` and assert URI-to-path maps for simple, HA, federated, and federated-HA configurations.
- EC tests use `StripedFileTestUtil`, `ClientProtocol`, and `waitForUpdatedStorageType(...)`.
- Secure tests use `MiniKdc`, SSL config, keytab/principal config, and `UserGroupInformation`.
- Pinned-block tests use `InternalDataNodeTestUtils.mockDatanodeBlkPinning`.
- Metrics tests read `DefaultMetricsSystem` counters/gauges for `BlocksScheduled`, `FilesProcessed`, `BytesMoved`, `BlocksMoved`, and `BlocksFailed`.

## Control Flow and Behavior
The class first proves duplicate scheduling is prevented by scheduling the same `DBlock`/`MLocation` twice and expecting the second call to return false. Movement tests write files under HOT/DISK, change policies to COLD/ARCHIVE or ONE_SSD, run `ToolRunner.run(conf, new Mover.Cli(), "-p", path)`, and wait for NameNode-reported storage types. Federation tests set up multiple namespaces, write opposite policies to each, and pass namespace-qualified paths to a single mover run. HA tests transition active NameNodes and use logical service URIs.

Failure and boundary tests check that unsatisfied policies with no target storage return `ExitStatus.NO_MOVE_BLOCK`, a simulated external SPS lock returns `ExitStatus.IO_EXCEPTION`, deleted block files trigger retry exhaustion with `NO_MOVE_PROGRESS`, and balancer max-iteration-time settings do not prematurely abort mover operations. Striped file tests move EC blocks from DISK to ARCHIVE, verify unsupported ONE_SSD is ignored for striped files, and ensure maintenance-state location filtering does not corrupt striped internal block indexing. Security flow starts a KDC, writes keytab and SSL settings, logs in with the mover principal, and reuses the locality movement test under `doAs`.

## State and Persistence
Each test creates HDFS namespace state, block files, block placement metadata, DataNode storage directories, and sometimes additional DataNodes. Storage policy changes persist in the namespace and are observed through `ClientProtocol.getBlockLocations` or DFS client located blocks. Security tests mutate global UGI state and explicitly reset it in `finally`. Metrics tests register mover sources in the process-wide metrics system. Pinned tests modify DataNode dataset behavior through mocks. Clusters are shut down in `finally` blocks to release on-disk MiniDFSCluster state.

## Dependencies and Integration Points
The suite spans `MiniDFSCluster`, `DistributedFileSystem`, `Mover`, `Mover.Cli`, `NameNodeConnector`, `DFSUtil`, `DFSTestUtil`, storage policy constants, balancer `ExitStatus`, DataNode internals, EC policy helpers, NameNode HA utilities, KDC/security/SSL helpers, Hadoop metrics, and low-level block-location APIs. It is a cross-component integration suite for NameNode policy metadata, DataNode storage movement, and CLI path resolution.

## Risks and Edge Cases
- Timing sensitivity is high: many tests rely on heartbeats, block reports, `GenericTestUtils.waitFor`, and short timeouts.
- Process-global UGI and metrics state can leak if cleanup fails.
- Federation URI iteration order is assumed only loosely in some tests, but path-map assertions still depend on resolved URI sets.
- EC and maintenance tests are sensitive to location array lengths and block-index mapping.
- Pinned and corrupted block tests depend on internal test hooks and DataNode storage implementation details.
- Long-running cluster movement tests are tagged slow and can be expensive in constrained CI.

## Test Signals
Signals include `ToolRunner` exit codes matching `ExitStatus`, exact storage type counts in located blocks, DataNode replace-block locality metric counters, CLI path-map contents, successful Kerberos keytab login, expected failure codes for pinned/corrupted blocks, EC striped block validation, and mover metrics counters/gauges after `Mover.run`.
