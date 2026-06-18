# Research Report: subset-b-007546

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/command/TestDiskBalancerCommand.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/command/TestDiskBalancerCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/NullConnector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/NullConnector.java

## Purpose
`NullConnector` is a minimal in-memory `ClusterConnector` implementation for DiskBalancer tests. It lets tests assemble a synthetic cluster by directly adding `DiskBalancerDataNode` instances without reading from NameNode RPCs, JSON, or other persistent sources.

## Important APIs, Types, and Functions
- `NullConnector implements ClusterConnector`.
- `private final List<DiskBalancerDataNode> nodes = new LinkedList<>()` stores the mutable in-memory cluster.
- `getNodes()` returns the backing list directly.
- `getConnectorInfo()` returns a fixed human-readable description identifying no persistence.
- `addNode(DiskBalancerDataNode node)` appends a node to the backing list.

## Control Flow and Behavior
There is no initialization or external discovery. Test code creates the connector, calls `addNode` for each synthetic node, and consumers call `getNodes` to read the same list. Returning the backing list means callers can observe all additions and can also mutate the connector state indirectly.

## State and Persistence
All state is process-local and in memory. There is no serialization, snapshotting, validation, synchronization, or defensive copying. The connector lifetime and data lifetime are the same Java object lifetime.

## Dependencies and Integration Points
The class depends only on DiskBalancer's `ClusterConnector` interface and `DiskBalancerDataNode` model type plus standard Java `List`/`LinkedList`. It integrates with `DiskBalancerCluster` or planner tests that need a connector-shaped source of nodes.

## Risks and Edge Cases
- `getNodes()` exposes the mutable list; callers can clear, reorder, or add invalid/null nodes.
- `addNode` accepts null and duplicates unless callers prevent them.
- `LinkedList` plus no synchronization makes this unsuitable for concurrent mutation.
- Because it is test-only, lack of persistence and validation is intentional but should not be copied into production connectors.

## Test Signals
Useful tests would confirm nodes added via `addNode` are returned by `getNodes`, that connector info is stable, and that DiskBalancer components can consume the connector without external cluster dependencies. Existing coverage is likely indirect through DiskBalancer data-model and planner tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/NullConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/TestNodePlan.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/TestNodePlan.java

## Purpose
`TestNodePlan` verifies `NodePlan` JSON serialization/deserialization and, more importantly, the security allowlist around polymorphic `Step` classes in serialized plans. It ensures only approved step classes can be deserialized from plan JSON.

## Important APIs, Types, and Functions
- `testNodePlan()` creates a `NodePlan`, adds a `MoveStep`, serializes with `toJson()`, and parses with `NodePlan.parseJson(...)`.
- `testNodePlanWithDisallowedStep()`, `testNodePlanWithSecondStepDisallowed()`, and `testNodePlanWithNestedDisallowedStep()` add unapproved `Step` implementations and require parse failure.
- `assertNodePlanInvalid(...)` expects `IOException` containing `Invalid @class value in NodePlan JSON`.
- `NestedStep` is a private test `Step` implementation with a Jackson `@JsonProperty` `NodePlan` field to verify nested object validation, not only top-level step validation.

## Control Flow and Behavior
The success path builds a plan with a concrete `MoveStep`, populates bandwidth, bytes, ideal storage, max disk errors, and volume-set ID, then confirms the JSON is parseable. The failure paths serialize `SampleStep` or `NestedStep` instances into `NodePlan` JSON and then call the real parser. The parser is expected to inspect `@class` metadata and reject any class not explicitly allowed, including disallowed classes after a valid first step and disallowed classes nested inside another serialized step.

## State and Persistence
The only persisted representation here is the JSON string generated by `NodePlan.toJson()`. No files are written. The tests exercise serialization state that later DiskBalancer CLI plan files rely on, so parser hardening is the persistent contract under test.

## Dependencies and Integration Points
The class depends on `NodePlan`, `MoveStep`, `Step`, `DiskBalancerVolume`, Jackson annotations, Hadoop `LambdaTestUtils`, and `SampleStep` test support. It integrates with DiskBalancer plan execution because CLI-generated plan files are parsed before being submitted or executed.

## Risks and Edge Cases
- The test is security-sensitive: loosening Jackson polymorphic validation could permit arbitrary or unexpected classes in plan JSON.
- `NestedStep` methods return defaults and nulls because behavior is irrelevant; only serialization shape matters.
- The tests assert exception text, so parser message changes can break them.
- They do not validate semantic equality of a valid parsed `MoveStep`; they only assert non-null parse success.

## Test Signals
The primary signal is `LambdaTestUtils.intercept(IOException.class, "Invalid @class value in NodePlan JSON", ...)`. A valid `MoveStep` round-trip returning non-null confirms the allowlist still permits expected DiskBalancer plans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/TestNodePlan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestMover.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestMover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestStorageMover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestStorageMover.java

## Purpose
`TestStorageMover` is a slow test suite for archival storage migration through `Mover.run`. It focuses on namespace-wide and path-scoped policy satisfaction, reusable synthetic namespace/cluster layouts, open-file safety, movement after renames, snapshots, and storage-full fallback behavior.

## Important APIs, Types, and Functions
- Static configuration sets block size, heartbeat/redundancy intervals, mover moved-window, and default storage-policy-satisfier mode.
- `NamespaceScheme` describes directories, files, file size, snapshots, and per-path `BlockStoragePolicy`; `prepare(...)` creates namespace objects and snapshots, while `setStoragePolicy(...)` applies policies.
- `ClusterScheme` describes cluster size, replication, storage type matrix, and capacities.
- `MigrationTest` encapsulates cluster setup, namespace preparation, mover execution, verification, replication checks, and cleanup.
- `MigrationTest.verifyRecursively(...)` walks the namespace using `listPaths` and verifies files with `Mover.StorageTypeDiff`.
- `PathPolicyMap` creates `/hot`, `/warm`, and `/cold` directories and can rename files among them to force policy changes after initial placement.
- `setVolumeFull(...)` mutates `FsVolumeImpl` capacity for a selected `StorageType`.

## Control Flow and Behavior
Most tests instantiate a `NamespaceScheme` and `ClusterScheme`, then call `MigrationTest.runBasicTest`: start the cluster, prepare files, verify initial state, set storage policies, run mover, and verify policy satisfaction. `testMigrateFileToArchival` moves a file to COLD. `testMoveSpecificPaths` runs `Mover.Cli.getNameNodePathsToMove` with `/foo/bar` and `/foo2` and verifies only the selected scopes. `testMigrateOpenFileToArchival` appends to an open file, runs migration, checks the under-construction block still has one location, continues writing, and reads back appended content. `testHotWarmColdDirs` initially satisfies policies, renames files across policy directories, reruns mover, and verifies the new layout.

Capacity tests fill either all DISK or all ARCHIVE volumes by setting volume capacities to zero and triggering heartbeats. When DISK is full, increasing replication for HOT can fall back to ARCHIVE, while COLD remains ARCHIVE-only; moving HOT to WARM can produce `NO_MOVE_BLOCK`. When ARCHIVE is full, increasing replication for COLD cannot add replicas, HOT file creation still works, and moving a COLD file to WARM can succeed because WARM allows DISK.

## State and Persistence
The tests create HDFS namespace objects, snapshots, file blocks, storage policy xattrs/metadata, and MiniDFSCluster storage directories. Verification forces block reports from each DataNode to synchronize NameNode state before checking locations. Open-file testing preserves an under-construction block across mover execution and validates subsequent writes. Capacity mutation is test-only in-memory state on `FsVolumeImpl`, communicated to the NameNode through heartbeats.

## Dependencies and Integration Points
The class integrates `MiniDFSCluster`, `DistributedFileSystem`, `Mover`, `Mover.Cli`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `DirectoryListing`, `HdfsLocatedFileStatus`, `LocatedBlock`, `DataNodeTestUtils`, `FsDatasetSpi`/`FsVolumeImpl`, `SnapshotTestHelper`, `Dispatcher`, `BlockPlacementPolicy`, and balancer `ExitStatus`. It tests interactions among policy selection, block placement, DataNode volume capacity, and mover scheduling.

## Risks and Edge Cases
- `verifyRecursively` lists one partial directory listing and does not paginate beyond the returned partial listing; this is acceptable for small test namespaces but would be unsafe as a general utility.
- `Thread.sleep(5000)` after mover runs is a coarse synchronization point.
- Direct `FsVolumeImpl.setCapacityForTesting(0)` depends on concrete dataset implementation.
- Open-file behavior is subtle: migrating completed blocks must not disturb the current under-construction block.
- The static `DEFAULT_CONF` is mutable and shared across tests.

## Test Signals
Signals include `Mover.run` returning expected `ExitStatus`, `Mover.StorageTypeDiff.removeOverlap(true)` proving storage types satisfy policy choices, replication count checks by storage type, successful reads after open-file migration, and policy ID verification for selected files after no-space movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestStorageMover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/AclTestHelpers.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/AclTestHelpers.java

## Purpose
`AclTestHelpers` is a small final utility class for NameNode ACL tests. It reduces boilerplate for constructing `AclEntry` instances and asserting permission/access-control outcomes.

## Important APIs, Types, and Functions
- Four overloaded `aclEntry(...)` factory methods build `AclEntry` values with combinations of scope, type, optional name, and optional permission.
- `assertFilePermissionDenied(FileSystem, UserGroupInformation, Path)` expects `DFSTestUtil.readFileBuffer` to throw `AccessControlException`.
- `assertFilePermissionGranted(...)` expects the same read to succeed and fails on `AccessControlException`.
- `assertPermission(FileSystem, Path, short)` delegates to the four-argument overload and infers `hasAcl` from bit 12 of the supplied mode.
- `assertPermission(FileSystem, Path, short, boolean)` masks expected mode to `01777`, reads `FileStatus`, compares `FsPermission.toShort()`, and checks `FileStatus.hasAcl()`.

## Control Flow and Behavior
ACL entry helpers simply configure an `AclEntry.Builder` and call `build`. Permission helpers perform real filesystem operations. The denied/granted helpers use exception control flow around file reads, while mode checks use `FileSystem.getFileStatus`.

## State and Persistence
The class has no state. It observes external HDFS state through `FileSystem` and `FileStatus`. It does not mutate permissions or ACLs itself.

## Dependencies and Integration Points
It depends on Hadoop filesystem, permission, ACL, security, and test utilities plus JUnit assertions. It is used heavily by `FSAclBaseTest` and likely other NameNode ACL suites through static imports.

## Risks and Edge Cases
- `assertPermission(fs, path, perm)` infers `hasAcl` from an encoded high bit convention; callers must pass the extended permission short intentionally.
- Access helpers only test read access through `DFSTestUtil.readFileBuffer`, not write, execute, or traversal permissions.
- Fail messages include the `UserGroupInformation`, which helps diagnosis but does not verify that the `FileSystem` is actually bound to that user.

## Test Signals
This helper contributes signals to ACL tests by making expected `AccessControlException`, exact mode bits, and `hasAcl` status concise and consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/AclTestHelpers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/CreateEditsLog.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/CreateEditsLog.java

## Purpose
`CreateEditsLog` is a test utility executable that synthesizes a NameNode edit log containing many file-create operations. The generated edits can be copied into a NameNode storage directory and paired with simulated DataNode blocks for scale or compatibility testing.

## Important APIs, Types, and Functions
- Constants: `BASE_PATH`, default `EDITS_DIR`, mutable `edits_dir`, and `BLOCK_GENERATION_STAMP`.
- `addFiles(...)` logs a base directory, creates reusable `BlockInfoContiguous` entries, assigns sequential block IDs, logs per-file subdirectories, open-file operations, close-file operations, and periodic `logSync`.
- `usage`, `printUsageExit()`, and `printUsageExit(String)` print CLI help and terminate with `System.exit(-1)`.
- `main(String[])` parses `-f numFiles startingBlockId numBlocksPerFile`, `-l blockSize`, `-r replication`, and `-d editsLogDirectory`, creates `current/`, opens a standalone edit log via `FSImageTestUtil.createStandaloneEditLog`, writes file operations, syncs, and closes.

## Control Flow and Behavior
The CLI validates required arguments, creates the edits directory and `current` subdirectory if needed, disables fsync for testing through `EditLogFileOutputStream.setShouldSkipFsyncForTesting(true)`, and opens an `FSEditLog` for the current layout version. `addFiles` first logs `BASE_PATH`, then for each file assigns a range of block IDs, creates an under-construction inode for `logOpenFile`, logs a completed inode with blocks through `logCloseFile`, creates a new subdirectory every `FileNameGenerator.getFilesPerDirectory()` files, and syncs every 2000 block IDs.

## State and Persistence
This utility writes real edit-log files under `edits_dir/current`. It mutates static `edits_dir`, toggles the static test fsync skip flag, and advances synthetic inode IDs and block IDs. File names encode block ID ranges so multiple non-overlapping generated logs can be combined conceptually. It does not create block files; it only creates namespace edit-log state.

## Dependencies and Integration Points
The utility depends on `FSEditLog`, `EditLogFileOutputStream`, `NameNodeLayoutVersion`, `FSImageTestUtil`, `INodeDirectory`, `INodeFile`, `INodeId`, `BlockInfoContiguous`, `FileNameGenerator`, and HDFS storage constants. It is related to DataNode simulation utilities that inject matching blocks.

## Risks and Edge Cases
- Argument parsing contains a risky condition `args[i].equals("-r") || args[i+1].startsWith("-")`; when `i` is the last index and not `-r`, this can access past the end.
- CLI errors call `System.exit`, making direct unit testing awkward.
- The generated edit log is tightly coupled to internal NameNode layout and inode/block constructors.
- `mkdir()` is used only one level at a time; parent path failures are not recovered.
- Fsync skipping is static and can affect later code in the same JVM if reused.

## Test Signals
There are no JUnit tests in this file. Operational signals are successful process exit, existence of non-empty edit-log files under `current/`, printed file/block counts, and later NameNode startup or edit-log loading with the generated operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/CreateEditsLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSAclBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSAclBaseTest.java

## Purpose
`FSAclBaseTest` is an abstract JUnit base suite for HDFS NameNode ACL semantics. It tests every major ACL mutation API, interaction with permission bits, default ACL inheritance, restart persistence, permission enforcement, effective access masks, and internal `AclFeature` deduplication/reference counting.

## Important APIs, Types, and Functions
- Static users `BRUCE`, `DIANA`, `BOB`, and `SUPERGROUP_MEMBER` model owner, non-owner, grouped user, and supergroup access.
- `startCluster()` enables `DFS_NAMENODE_ACLS_ENABLED_KEY` and starts a 1-DataNode `MiniDFSCluster`.
- Per-test `setUp()` creates a fresh path `/pN` and filesystem handles for each user; `destroyFileSystems()` closes them.
- Test groups cover `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `setPermission`, default ACL inheritance on new files/dirs/intermediate paths/symlinks, rename behavior, authorization checks, `FileSystem.access`, effective permissions, and deduplication.
- Helpers include `restartCluster()`, `assertAclFeature(...)`, `getAclFeature(...)`, and `assertPermission(...)`.

## Control Flow and Behavior
Mutation tests generally create a file or directory, set initial permissions and ACLs, call one ACL API, fetch `AclStatus`, compare exact returned ACL entries, assert extended permission bits, and inspect whether the backing inode has an `AclFeature`. Negative cases assert `FileNotFoundException` or `AclException` for missing paths and default ACLs on files. Sticky-bit tests verify ACL operations preserve sticky mode bits.

Inheritance tests set default ACLs on parent directories and then create child files, directories, intermediate paths, and symlinks. They verify that child files receive access ACLs when needed, child directories receive both access and default ACLs, minimal defaults can collapse to no `AclFeature` for files, access-only ACLs are not inherited, and renaming into an ACL-bearing directory does not apply inherited defaults retroactively. UMask tests toggle `FSDirectory.setPosixAclInheritanceEnabled` to compare legacy and POSIX ACL inheritance behavior.

Authorization tests create resources as `bruce`, then verify only owner, superuser, or supergroup members can mutate ACLs or read ACL status across traverse restrictions. Access tests check named user and named group precedence, including a named user deny overriding group grants. Effective-access tests validate that `AclStatus.getEffectivePermission` reflects the current mask after `setPermission`.

`testDeDuplication` restarts the cluster for a clean static `AclStorage` map, creates identical inherited ACLs across siblings and files, verifies reference-count reuse, verifies counts decrease on ACL mutation/removal/deletion, and checks behavior after loading edits and fsimage by restarting the NameNode and saving namespace.

## State and Persistence
The suite creates persistent HDFS namespace ACL metadata and repeatedly restarts clusters without formatting to verify edit-log/fsimage persistence. It also inspects internal inode state through `FSDirectory.getINode(..., DirOp.READ_LINK)` and `INode.getAclFeature`. Static `AclStorage.getUniqueAclFeatures()` is explicitly cleared for dedup tests. Configuration flags for permissions and POSIX ACL inheritance are temporarily changed and restored.

## Dependencies and Integration Points
The class depends on `MiniDFSCluster`, `FileSystem`, `DFSTestUtil`, `AclTestHelpers`, `AclStorage`, `AclFeature`, `FSDirectory`, `INode`, `FsPermissionExtension`, `AclStatus`, HDFS safe mode/saveNamespace RPCs, and Hadoop security `UserGroupInformation`. Subclasses provide concrete cluster initialization through this abstract base pattern.

## Risks and Edge Cases
- Many tests compare exact ACL entry arrays; ordering or canonicalization changes will break them.
- Static cluster/configuration/path state means subclasses must coordinate setup correctly.
- `testDeDuplication` manipulates static global ACL feature intern tables and has comments noting reference counts differ after restart within the same JVM.
- Permission bit assertions use extended ACL-bit encoding, so expected octal values are subtle.
- Tests that restart clusters and save namespaces are heavier and can expose unrelated MiniDFSCluster timing issues.

## Test Signals
Signals include exact `AclStatus` entry arrays, `FileStatus.hasAcl`, permission shorts, direct `AclFeature` presence/absence and immutable entries, restart-stable ACL lists, expected `AccessControlException`, successful/failed `FileSystem.access`, and deduplicated `AclFeature` unique-element counts and reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSAclBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSImageTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSImageTestUtil.java

## Purpose
`FSImageTestUtil` is a broad static utility class for NameNode fsimage and edits-log tests. It provides helpers for hashing images, mocking storage directories, creating standalone edit logs, counting edit-log operations, comparing NameNode storage directories, corrupting VERSION files, locating images/edits, and inspecting checkpoint state.

## Important APIs, Types, and Functions
- Hashing: `getFileMD5(...)`, `getImageFileMD5IgnoringTxId(...)`, and `getFileMD5s(...)`.
- Storage mocks: `mockStorageDirectory(File, NameNodeDirType)`, overloaded `mockStorageDirectory(StorageDirType, boolean, String...)`, and `mockFile(boolean)`.
- Edit logs: `createStandaloneEditLog(...)`, `createEditLogWithJournalManager(...)`, `createAbortedLogWithMkdirs(...)`, `countEditLogOpTypes(...)`, and `findLatestEditsLog(...)`.
- Image/storage comparison: `assertSameNewestImage(...)`, `assertParallelFilesAreIdentical(...)`, `assertPropertiesFilesSame(...)`, `assertFileContentsSame(...)`, `assertFileContentsDifferent(...)`, `assertNNFilesMatch(...)`.
- Discovery: `inspectStorageDirectory(...)`, `getCurrentDirs(...)`, `findLatestImageFile(...)`, `findNewestImageFile(...)`, `getNameNodeCurrentDirs(...)`, `getStorageTxId(...)`, and `getLatestImageSummary(...)`.
- Miscellaneous: `createEmptyInodeFile(...)`, `assertNNHasCheckpoints(...)`, `assertNNHasRollbackCheckpoints(...)`, `corruptVersionFile(...)`, `assertReasonableNameCurrentDir(...)`, `logStorageContents(...)`, `getFSImage(...)`, and `getNSQuota(...)`.

## Control Flow and Behavior
Hash helpers compute MD5s directly or copy an fsimage to a temp file, zero the txid field at byte offset 24, and hash the modified copy. Mock helpers use Mockito to return controlled `StorageDirectory` and `File` behavior for storage inspectors. Standalone edit-log creation clears a target directory, mocks `NNStorage`, builds `FSEditLog`, and initializes journals for write. Aborted-log creation writes a configured sequence of mkdir operations and aborts the current log segment.

Comparison helpers group files by name across parallel current directories, recurse into directories, ignore configured filenames, compare VERSION files as properties while optionally ignoring keys such as `storageID`, and compare other files by MD5. Checkpoint helpers iterate NameNode current directories and assert expected fsimage filenames are non-empty. VERSION corruption loads properties, changes or removes one key, and writes the file back.

## State and Persistence
The utility reads and writes real local files under NameNode storage directories and test temp directories. `createStandaloneEditLog` deletes existing log-dir contents. `getImageFileMD5IgnoringTxId` creates and deletes a temp copy. `corruptVersionFile` mutates VERSION files in place. Storage-inspection helpers observe persistent fsimage/edit-log filenames and transaction IDs. Mock storage methods create no disk state beyond the provided `File` objects.

## Dependencies and Integration Points
The class integrates with `NNStorage`, `StorageDirectory`, `FSImageTransactionalStorageInspector`, `FSEditLog`, `JournalManager`, `FileJournalManager`, `EditLogInputStream`, `MiniDFSCluster`, `NameNode`, `FSImage`, `FSImageUtil`, protobuf `FsImageProto.FileSummary`, `MD5FileUtils`, Mockito, Guava/thirdparty collections, and Hadoop IO utilities. It is central support for NameNode storage, checkpoint, rollback, bootstrap, and edit-log tests.

## Risks and Edge Cases
- `IMAGE_TXID_POS = 24` is a format-sensitive constant; fsimage header layout changes require updates.
- `createStandaloneEditLog` deletes directory contents, so callers must pass test-owned directories only.
- `assertParallelFilesAreIdentical` assumes `listFiles()` is non-null and recurses based on the first same-name file being a directory.
- Property comparison ignores only requested keys; timestamp or new generated properties can cause failures unless explicitly handled.
- Many helpers use assertions directly and are intended for tests, not production utilities.

## Test Signals
Signals include matching MD5 hashes, expected unique hash counts, non-empty fsimage checkpoint files, identical parallel NameNode storage contents, expected edit-log operation counts, reasonable current-directory structure, readable latest image summaries, and exact transaction IDs from storage metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSImageTestUtil.java -->
