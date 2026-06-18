# subset-b-007563 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdminMiniCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdminMiniCluster.java

## Purpose
`TestDFSHAAdminMiniCluster` is a MiniDFSCluster-backed integration test for `DFSHAAdmin` in an HA NameNode topology. It validates service-state queries, manual state transitions, observer transitions, failover, fencing configuration, health checks, safe-mode restrictions, and split-brain avoidance.

## Important APIs, Types, And Functions
The test uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology()`, `DFSHAAdmin`, `HAAdmin`, `NameNode`, `NameNodeAdapter`, `HAServiceState`, `DFSConfigKeys`, and shell fencing configuration. The helper `runTool(String...)` resets captured stderr, invokes `tool.run(args)`, stores `errOutput`, and returns the command status.

## Control Flow
`setup()` builds a two-NameNode HA cluster with zero DataNodes, enables `DFS_HA_NN_NOT_BECOME_ACTIVE_IN_SAFEMODE`, configures `DFSHAAdmin`, and records nn1's port for fencing assertions. Tests then drive command-line flows: `-getServiceState`, `-transitionToActive`, `-transitionToStandby`, `-transitionToObserver`, `-failover`, and `-checkHealth`. Fencing tests mutate `dfs.ha.fencing.methods`, run failover variants with `--forcefence` and `--forceactive`, and inspect a temp file written by the shell fencer. Safe-mode tests enter and leave safe mode through `NameNodeAdapter` and simulate `-forcemanual` confirmation by replacing `System.in`.

## State, Persistence, And Dependencies
State lives in the MiniDFSCluster HA NameNodes, safe-mode flags, a temporary fencer output file, captured stderr bytes, and transient `System.in` replacement. There is no long-term persistence beyond the temp file. The test depends on HA RPC behavior, shell command substitution, JUnit lifecycle cleanup, and platform-specific Windows versus POSIX shell syntax.

## Integration Points
This file tests `DFSHAAdmin` against real HDFS HA services rather than mocks. It exercises `HAAdmin` command parsing, NameNode HA protocol state changes, DFS HA fencing target substitution, safe-mode readiness checks, and observer-state semantics.

## Risks
The fencer assertion is sensitive to shell quoting, platform newline handling, and temp-file cleanup. Tests that replace `System.in` do not consistently restore it in all methods, which can leak into later tests if run order or failures change. HA state transitions and failovers are timing-sensitive, though most operations are synchronous through MiniDFSCluster helpers.

## Test Signals
Strong signals are exact command return codes, captured error text for safe-mode failures, direct `NameNode` state checks, nonempty fencer output only when fencing is forced, and the assertion that both NameNodes are never active at once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdminMiniCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSZKFailoverController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSZKFailoverController.java

## Purpose
`TestDFSZKFailoverController` validates DFS-specific ZooKeeper Failover Controller behavior for HA NameNodes. It covers auto failover, manual failover, bind-address selection, observer-state interaction, thread-dump capture on health changes, and startup with HDFS-backed credential-provider configuration.

## Important APIs, Types, And Functions
Key types include `DFSZKFailoverController`, `ZKFailoverController`, `ClientBaseWithFixes`, `MiniDFSCluster`, `MiniDFSNNTopology`, `ZKFCTestUtil`, `HealthMonitor`, `AlwaysSucceedFencer`, `HATestUtil`, `NamenodeProtocols`, and `TestingThread`. `startCluster()` creates a non-ephemeral-port HA topology, formats ZK, starts one ZKFC per NameNode, waits for health, and configures a failover-aware `FileSystem`.

## Control Flow
`setup()` configures a nameservice-scoped ZK quorum, fencer, auto failover, low IPC idle timeout, and explicit ZKFC ports. `startCluster()` starts nn1 and nn2, formats ZK, starts `ZKFCThread` instances, waits for nn1 to become active and both monitors to become healthy, then creates a failover filesystem. Tests shut down active NameNodes, restart nodes, call ZKFC proxies for graceful failover, invoke `DFSHAAdmin`, and poll both NameNode service state and ZKFC-local state with `GenericTestUtils.waitFor`.

## State, Persistence, And Dependencies
State spans the external test ZooKeeper from `ClientBaseWithFixes`, MiniDFSCluster NameNode process state, ZKFC election state, fencer last-target state, and actual HDFS namespace paths. Threads are managed through `TestContext` and interrupted in teardown. The static block disables edit-log fsync for speed.

## Integration Points
The test connects HDFS HA, ZooKeeper election/health monitoring, fencing, DFSHAAdmin, Web/IPC bind-address config, credential providers, and observer-state access control. It verifies that Observer NameNodes reject ZKFC-originated standby transitions and avoid active election.

## Risks
The tests depend on local port availability despite using `ServerSocketUtil.getPort`, and on timing-sensitive failover and health monitor polling. `System.in` is replaced in manual observer transition tests and must be restored on exceptional paths. ZooKeeper state and ZKFC threads require robust cleanup to avoid cross-test interference.

## Test Signals
Signals include NameNode HA state reaching ACTIVE/STANDBY/OBSERVER, successful file existence across failovers, fencer last-target addresses, expected RPC bind host, intercepted `AccessControlException`, captured ZKFC thread dump state, and election participation flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSZKFailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDebugAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDebugAdmin.java

## Purpose
`TestDebugAdmin` exercises HDFS `DebugAdmin` subcommands for lease recovery, block metadata verification, metadata recomputation, and erasure-coded file verification.

## Important APIs, Types, And Functions
The file uses `DebugAdmin`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `FsDatasetSpi`, `ExtendedBlock`, `LocatedStripedBlock`, `StripedBlockUtil`, `SystemErasureCodingPolicies`, `FsDatasetTestUtil.getBlockFile/getMetaFile`, and Apache Commons `FileUtils`. `runCmd(String[])` redirects both stdout and stderr, invokes `admin.run`, and normalizes line separators into a single assertion string.

## Control Flow
Each test starts an appropriate MiniDFSCluster, creates files, locates block and metadata files from DataNode datasets, runs debug commands, and asserts exact return/status output. `testVerifyECCommand` creates an EC directory, verifies many file sizes, corrupts local striped block bytes, recomputes checksums with `computeMeta`, and verifies that `verifyEC` reports mismatched EC compute results. It also tests `-blockId` and `-skipFailureBlocks`.

## State, Persistence, And Dependencies
State includes local block files, metadata checksum files, HDFS file lease state, EC policy settings, and captured process streams. The test mutates DataNode local storage directly to create corruption and writes output metadata under a test root. Cluster teardown is the main cleanup path.

## Integration Points
This bridges CLI argument handling with DataNode on-disk block layout, metadata checksum readers/writers, lease recovery APIs, HDFS EC placement, and striped block parsing.

## Risks
The EC corruption test is highly coupled to block placement, local DataNode storage paths, block-group parsing, and exact DebugAdmin output text. Directly replacing block files and deleting meta files can leave cluster state inconsistent if assertions fail mid-test. Output normalization removes line separators, so regressions in formatting may be obscured if text still concatenates similarly.

## Test Signals
Signals include exact help/error strings and return codes, created metadata file existence and length, successful checksum verification, "All EC block group status: OK", and error output for intentionally corrupted EC data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDebugAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDelegationTokenFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDelegationTokenFetcher.java

## Purpose
`TestDelegationTokenFetcher` verifies token fetch, save, renew, cancel, print, null-token, and failure paths for `DelegationTokenFetcher` over WebHDFS and RPC.

## Important APIs, Types, And Functions
The test uses `DelegationTokenFetcher`, `WebHdfsFileSystem`, `DistributedFileSystem`, `MiniDFSCluster`, `Credentials`, `Token<DelegationTokenIdentifier>`, `FakeRenewer`, `LocalFileSystem`, Mockito stubbing, and `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`.

## Control Flow
Mock-based tests force `getDelegationToken` to throw, return a concrete token, or return null, then call `saveDelegationToken` and inspect the token storage file. The RPC test starts a zero-DataNode cluster with delegation tokens always enabled, fetches a token without a renewer, prints it in verbose and nonverbose modes, and confirms renewal fails with an `AccessControlException`.

## State, Persistence, And Dependencies
Token state is persisted to temporary local token files via `Credentials.writeTokenStorageFile` behavior. `FakeRenewer` captures last renewed/canceled tokens. The MiniDFSCluster path depends on HDFS security token configuration even in a test cluster.

## Integration Points
The file links WebHDFS token retrieval, HDFS RPC token retrieval, Hadoop credentials serialization, token renewer plugins, and user-visible token-print formatting.

## Risks
Mockito coverage validates fetcher logic without a real HTTP server for most WebHDFS paths. The expected nonverbose prefix includes the process user name and empty renewer, so it is sensitive to token display format changes. Raw `Token` use in the RPC test suppresses type specificity.

## Test Signals
Signals include thrown `IOException` on fetch failure, byte-for-byte token identifier/password equality after storage reload, `FakeRenewer` renew/cancel captures, absence of a file for null token, and a renewal denial message for tokens without renewers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDelegationTokenFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestECAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestECAdmin.java

## Purpose
`TestECAdmin` covers `ECAdmin` command behavior that is difficult to express in the generic CLI suite, mainly cluster-topology validation and user-facing output for enabling or verifying erasure coding policies.

## Important APIs, Types, And Functions
The file uses `ECAdmin`, `DFSTestUtil.setupCluster`, `MiniDFSCluster`, system EC policies from `SystemErasureCodingPolicies`, and captured `System.out`/`System.err`. Helpers `assertNotEnoughDataNodesMessage`, `assertNotEnoughRacksMessage`, `resetOutputs`, and `runCommandWithParams` centralize command execution and output checks.

## Control Flow
Tests redirect standard streams in `setup()`, create clusters with specific DataNode and rack counts, enable or disable policies through the filesystem, run `-verifyClusterSetup` or `-enablePolicy`, and assert return codes plus stdout/stderr contents. They cover insufficient DataNodes, insufficient racks, successful topologies, no enabled EC policies, invalid policy names, too many positional arguments, and missing `-policy` values.

## State, Persistence, And Dependencies
State lives in cluster topology, enabled EC policy state, and captured stream buffers. There is no durable persistence outside the cluster. Teardown restores streams and shuts down clusters.

## Integration Points
The test connects `ECAdmin` CLI parsing with NameNode EC policy management and topology/rack validation logic.

## Risks
The assertions are message-substring based but still tied to exact policy names and wording. Shared `System.out`/`System.err` replacement can affect other tests if teardown is skipped. Cluster topology helper behavior determines whether rack counts are realistic.

## Test Signals
Signals are command return codes `0`, `2`, `1`, or `-1`, expected topology-warning messages, empty stderr on normal validation, and explicit RemoteException text for unknown policy names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestECAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetConf.java

## Purpose
`TestGetConf` validates the `GetConf` tool across non-federated, federated, HA, journal-node, include/exclude host-file, and internal-nameservice configurations.

## Important APIs, Types, And Functions
It uses `GetConf`, `GetConf.Command`, `CommandHandler`, `ToolRunner`, `HdfsConfiguration`, `DFSUtil`, `ConfiguredNNAddress`, `NetUtils`, `HostsFileWriter`, and many `DFSConfigKeys`. Helpers synthesize nameservices, per-nameservice address keys, static host resolutions, DFSUtil-derived expected addresses, and GetConf output tokenization.

## Control Flow
Tests create targeted `HdfsConfiguration` instances, populate config keys, derive expected values through `DFSUtil`, run `GetConf` with the matching command, and compare output. The journal-node test walks through direct shared-edits URIs, federation with HA suffixes, missing journal nodes, non-qjournal file URIs, unknown hosts, and malformed URI strings. Other tests verify invalid arguments, missing keys, `-confKey`, extra arguments, include/exclude file commands, and filtering by `dfs.internal.nameservices`.

## State, Persistence, And Dependencies
Most state is in-memory configuration. Host resolution is modified through `NetUtils.addStaticResolution`. Include/exclude tests create local files through `HostsFileWriter` under MiniDFSCluster's base directory and clean them up explicitly.

## Integration Points
This test aligns `GetConf` output with `DFSUtil` cluster-address resolution, qjournal URI parsing, Hadoop static DNS resolution, and HDFS host-provider configuration.

## Risks
Journal-node expected strings are built from `HashSet` iteration order, so equality can be order-sensitive if the set order changes between expected and actual paths. Static host-resolution additions are process-global. The `remoteNsCount` variable is unused, and a couple method names use uppercase `Test...` style.

## Test Signals
Signals are successful versus failed `ToolRunner` return codes, output matching DFSUtil-derived addresses, usage text for invalid commands, thrown `UnknownHostException`/`URISyntaxException`, and exact include/exclude path output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetGroups.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetGroups.java

## Purpose
`TestGetGroups` supplies the HDFS-specific implementation for the generic `GetGroupsTestBase`, verifying group lookup behavior against a MiniDFSCluster NameNode.

## Important APIs, Types, And Functions
It extends `GetGroupsTestBase`, creates an `HdfsConfiguration`, starts a zero-DataNode `MiniDFSCluster`, and overrides `getTool(PrintStream)` to return `new GetGroups(conf, o)`.

## Control Flow
`setUpNameNode()` initializes the cluster before inherited tests run. `tearDownNameNode()` shuts it down. The actual test methods and assertions are inherited from `GetGroupsTestBase`, using the returned HDFS `GetGroups` tool.

## State, Persistence, And Dependencies
State is limited to the MiniDFSCluster and inherited `conf` field. There is no persistent filesystem content.

## Integration Points
This ties the common Hadoop group CLI test suite to the HDFS NameNode-backed `GetGroups` implementation.

## Risks
Because behavior is inherited, local readability depends on the base class. Failures may originate from user/group mapping environment differences or HDFS service startup rather than code in this file.

## Test Signals
The effective signals come from `GetGroupsTestBase`: command output and return codes for user-to-group lookup using the HDFS tool instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestGetGroups.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicyCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicyCommands.java

## Purpose
`TestStoragePolicyCommands` verifies `StoragePolicyAdmin` set, get, and unset command behavior against HDFS paths, including URI-qualified paths and missing-path failures.

## Important APIs, Types, And Functions
The class uses `StoragePolicyAdmin`, `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.toolRun`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `StorageType`, and `StoragePolicySatisfierMode.EXTERNAL`.

## Control Flow
`clusterSetUp()` creates a one-DataNode cluster with ARCHIVE and DISK storage types and an external SPS mode. Tests create nested files, run storage policy commands with absolute and URI-qualified paths, compare expected command output for WARM/COLD/HOT policies, unset policies, and verify unspecified-policy output after unsetting.

## State, Persistence, And Dependencies
State is HDFS namespace metadata: explicit storage policies on directories/files and default unspecified policies. Cluster and filesystem are closed in teardown.

## Integration Points
The test covers `StoragePolicyAdmin` CLI parsing, filesystem path qualification, NameNode storage-policy metadata APIs, and default policy suite string formatting.

## Risks
Expected output includes `BlockStoragePolicy.toString()` formatting and exact path qualification. The static `conf`, `cluster`, and `fs` fields support subclass reuse but can leak if teardown fails.

## Test Signals
Signals are `DFSTestUtil.toolRun` return codes, expected success messages, policy descriptions from `BlockStoragePolicySuite`, missing path errors, and unspecified-policy output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicyCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicySatisfyAdminCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicySatisfyAdminCommands.java

## Purpose
`TestStoragePolicySatisfyAdminCommands` validates the `-satisfyStoragePolicy` admin command with an external Storage Policy Satisfier, both for raw HDFS paths and URI-qualified paths.

## Important APIs, Types, And Functions
It uses `StoragePolicyAdmin`, `StoragePolicySatisfier`, `ExternalSPSContext`, `NameNodeConnector`, `DFSTestUtil.getNameNodeConnector`, `DFSTestUtil.waitExpectedStorageType`, `DistributedFileSystem`, and `StoragePolicySatisfierMode.EXTERNAL`.

## Control Flow
Setup enables external SPS mode, reduces the SPS DataNode cache refresh interval, starts a one-DataNode ARCHIVE/DISK cluster, obtains a `NameNodeConnector`, initializes a `StoragePolicySatisfier`, and starts it. Each test creates a file, confirms unspecified policy, sets COLD, runs `-satisfyStoragePolicy`, and waits for the block to move to ARCHIVE.

## State, Persistence, And Dependencies
State includes HDFS file block placement, storage policy metadata, the external SPS service thread, NameNode connector state, and DataNode storage-type reports. The field `externalSps` is intended for teardown but setup declares a local variable with the same name, so the field remains null and the satisfier may not be stopped explicitly.

## Integration Points
This tests CLI scheduling through NameNode APIs and the external SPS mover pipeline that changes block storage type.

## Risks
The shadowed `externalSps` local variable is a cleanup bug and can leak a service thread until cluster shutdown. The wait is timing-sensitive and depends on a single DataNode advertising ARCHIVE. URI-qualified expected output is exact-string sensitive.

## Test Signals
Signals include command return codes and messages, successful COLD policy set, scheduling output, and `waitExpectedStorageType` observing one ARCHIVE replica within 30 seconds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicySatisfyAdminCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFSStoragePolicyCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFSStoragePolicyCommands.java

## Purpose
`TestViewFSStoragePolicyCommands` reuses the storage-policy command suite with a ViewFileSystem default filesystem and adds ViewFS-specific root and scheme-qualified path coverage.

## Important APIs, Types, And Functions
It extends `TestStoragePolicyCommands` and uses `MiniDFSNNTopology.simpleFederatedTopology`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_SCHEME`, `DistributedFileSystem`, `WebHDFS` URI construction, and `StoragePolicyAdmin`.

## Control Flow
The overridden setup starts a federated two-NameNode cluster, creates `/user1` and `/user2` on separate filesystems, sets `fs.defaultFS` to `viewfs://cluster`, mounts `/foo` and `/hdfs2`, and initializes `fs = FileSystem.get(conf)`. Additional tests assert that storage-policy operations on `/` fail under ViewFS, and that hdfs:// and webhdfs:// URI-qualified paths still support set/get/unset.

## State, Persistence, And Dependencies
State is in the ViewFS mount table and underlying HDFS namespace. It inherits static cluster/fs fields from the base class and relies on base teardown.

## Integration Points
The test checks `StoragePolicyAdmin` behavior through ViewFS mount resolution, federated HDFS targets, direct HDFS URI handling, and WebHDFS path handling.

## Risks
Root failure output is tied to ViewFS exception wording. WebHDFS URI construction uses the NameNode HTTP host and port, which depends on MiniDFSCluster HTTP setup. Inherited base tests now execute against ViewFS-mounted paths, so failures can originate from mount resolution rather than storage policy logic.

## Test Signals
Signals include root command failure with "not supported for filesystem viewfs", inherited storage-policy command successes, and explicit set/get/unset output for hdfs:// and webhdfs:// paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFSStoragePolicyCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithDFSAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithDFSAdmin.java

## Purpose
`TestViewFileSystemOverloadSchemeWithDFSAdmin` verifies that `DFSAdmin` commands operate correctly when the `hdfs` scheme is overloaded by `ViewFileSystemOverloadScheme` with configured mount links.

## Important APIs, Types, And Functions
It uses `ViewFileSystemOverloadScheme`, `ViewFsTestSetup.addMountLinksToConf`, `DFSAdmin`, `ToolRunner`, `MiniDFSCluster`, `DistributedFileSystem`, `CommonConfigurationKeys`, and captured stdout/stderr helpers `assertOutMsg`/`assertErrMsg`.

## Control Flow
Setup configures `fs.hdfs.impl` to ViewFS overload and the target HDFS implementation to `DistributedFileSystem`, starts a cluster, and records the default hdfs URI. Tests add HDFS and local mount links, then run `DFSAdmin` with and without `-fs` for `-safemode`, `-saveNamespace`, `-allowSnapshot`, `-disallowSnapshot`, and `-setBalancerBandwidth`. Negative tests use an unknown host target and a local filesystem mount.

## State, Persistence, And Dependencies
State includes the ViewFS mount table in configuration, the MiniDFSCluster NameNode state, local target directory, safe-mode state, snapshot permission state, and captured stream buffers. `FileSystem.closeAll()` is called during teardown.

## Integration Points
This covers DFSAdmin command dispatch through an overloaded `hdfs` scheme, fallback target FS behavior, mounted local filesystem rejection, and administrative RPCs reaching the underlying HDFS filesystem.

## Risks
It assumes the default filesystem URI's host names the mount table. Error and success assertions depend on output line positions. Safe mode is entered and left in tests, so cleanup after failures matters for later tests.

## Test Signals
Signals include return codes, "Save namespace successful", safe-mode status, UnknownHostException text, local filesystem rejection text, snapshot command success messages, and balancer bandwidth output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithDFSAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithFSCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithFSCommands.java

## Purpose
`TestViewFileSystemOverloadSchemeWithFSCommands` verifies FsShell behavior for `-df` when the `hdfs` scheme is backed by `ViewFileSystemOverloadScheme`.

## Important APIs, Types, And Functions
It uses `ViewFileSystemOverloadScheme`, `ViewFsTestSetup.addMountLinksToConf`, `FsShell`, `ToolRunner`, `MiniDFSCluster`, and stream scanning helpers.

## Control Flow
Setup mirrors the DFSAdmin overload test: configure `fs.hdfs.impl`, target HDFS implementation, start a cluster, and capture the default HDFS URI. The test adds two mounts, one HDFS and one local, runs `FsShell -df -h` against the overloaded root, parses stdout lines, and removes observed mount paths from an expected list.

## State, Persistence, And Dependencies
State is the configured mount table, local target directory, MiniDFSCluster, and captured stdout/stderr. The `FsShell` is closed in a finally block.

## Integration Points
This validates FsShell filesystem resolution and per-mount disk-usage listing through ViewFS overload, including mixed HDFS/local targets.

## Risks
The test expects exactly three output lines and assumes the final whitespace-separated token is the mount path. Formatting changes in `-df -h` can break it without a semantic regression. It only covers `-df`, not other FsShell commands.

## Test Signals
Signals are zero return code, output line count, and both configured mounts appearing in the `df` result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithFSCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestWebHDFSStoragePolicyCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestWebHDFSStoragePolicyCommands.java

## Purpose
`TestWebHDFSStoragePolicyCommands` runs the base storage-policy command tests using a WebHDFS filesystem as the default filesystem.

## Important APIs, Types, And Functions
It extends `TestStoragePolicyCommands` and uses `WebHdfsTestUtil.getWebHdfsFileSystem`, `WebHdfsConstants.WEBHDFS_SCHEME`, and `FS_DEFAULT_NAME_KEY`.

## Control Flow
The overridden setup calls the base HDFS cluster setup, replaces `fs` with a WebHDFS filesystem, and points `fs.defaultFS` at its URI. The inherited tests then execute set/get/unset policy commands through WebHDFS paths.

## State, Persistence, And Dependencies
State is inherited from the base cluster and stored through WebHDFS calls into the same NameNode namespace. Base teardown closes the filesystem and cluster.

## Integration Points
This connects `StoragePolicyAdmin` to WebHDFS path resolution and REST-backed filesystem operations while reusing the HDFS storage-policy assertions.

## Risks
Because it only overrides setup, diagnosis requires understanding the base class. WebHDFS server availability and URI qualification can cause failures outside storage-policy metadata logic.

## Test Signals
Signals are inherited from `TestStoragePolicyCommands`: successful set/get/unset operations, missing-path failures, and policy/unspecified output, all executed with WebHDFS as default FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestWebHDFSStoragePolicyCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TestOfflineEditsViewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TestOfflineEditsViewer.java

## Purpose
`TestOfflineEditsViewer` validates Offline Edits Viewer processors for generated and stored edit logs, including binary/XML round trips, recovery mode for truncated logs, stats output, help handling, and processor/input format validation.

## Important APIs, Types, And Functions
It uses `OfflineEditsViewer`, `OfflineEditsViewer.Flags`, `OfflineEditsViewerHelper`, `StatisticsEditsVisitor`, `FSEditLogOpCodes`, `NameNodeLayoutVersion`, `DFSTestUtil`, and `FileUtils`. Helpers include `runOev`, `hasAllOpCodes`, and `filesEqualIgnoreTrailingZeros`.

## Control Flow
Lifecycle starts a helper MiniDFSCluster before each test and shuts it down after each test. Tests generate edits, convert binary to XML and back, compare reparsed binary while tolerating trailing invalid-op padding, and verify that generated/stored logs cover all non-skipped opcodes. Recovery mode truncates the edit file, confirms normal parse fails, then parses with recovery and round-trips to XML. Additional tests inspect help output, stats string entries for null opcode counts, and reject binary-to-binary or XML-to-XML processor misuse.

## State, Persistence, And Dependencies
State includes generated edits under the helper cluster directory, checked-in cache data files, temp output files, and stats files. `filesEqualIgnoreTrailingZeros` mutates the in-memory layout-version byte to current layout for comparison compatibility.

## Integration Points
This tests edit log generation, OEV binary/XML/stats processors, recovery parsing, edit opcode accounting, and compatibility with stored golden edit logs.

## Risks
Opcode coverage depends on `OfflineEditsViewerHelper.generateEdits()` keeping pace with new edit opcodes and the skip list. Stored golden files under `test.cache.data` must exist. Comparison intentionally ignores trailing invalid-op bytes and layout-version drift, which is useful for compatibility but can hide some binary differences.

## Test Signals
Signals include OEV return codes, opcode count coverage, XML golden-file equality ignoring EOLs, binary equality ignoring trailing invalid ops, help output without parse errors, and stats strings containing zero counts for missing opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TestOfflineEditsViewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewer.java

## Purpose
`TestOfflineImageViewer` is the broad integration test for Offline Image Viewer PB processors. It builds one rich fsimage and validates file distribution, XML rendering, WebImageViewer WebHDFS endpoints, delimited output, parallel delimited output, corruption detection, ReverseXML reconstruction, CLI option handling, and EC policy serialization.

## Important APIs, Types, And Functions
The file uses `OfflineImageViewerPB`, `PBImageXmlWriter`, `PBImageDelimitedTextWriter`, `PBImageCorruptionDetector`, `PBImageCorruption`, `OfflineImageReconstructor`, `FileDistributionCalculator`, `WebImageViewer`, `FSImageLoader`, `MiniDFSCluster`, `FSImageTestUtil`, `MD5FileUtils`, protobuf `FsImageProto`, and XML DOM/SAX helpers. It also constructs sample inode protobufs for focused delimited-entry tests.

## Control Flow
`createOriginalFSImage()` runs once, sets UTC timezone, starts a cluster with delegation tokens, ACLs, parallel image load settings, EC policies, custom EC policy options, directories, files, XML-sensitive path names, sticky-bit directory, delegation tokens, snapshots, xattrs, ACLs, and EC files. It saves namespace and records the latest fsimage. Tests then visit that fsimage with different processors, parse output, run embedded WebImageViewer HTTP/WebHDFS operations, create corrupted fsimages by XML deletion plus ReverseXML, compare expected corruption CSV resources, and perform XML round trips.

## State, Persistence, And Dependencies
Global static state includes `originalFsimage`, `tempDir`, `writtenFiles`, `dirCount`, EC file counts, added EC policy name, and timezone. Output files, SQLite/in-memory processor DB paths, XML files, corrupted image files, and MD5s live under test directories. `deleteOriginalFSImage()` deletes temp storage and restores timezone.

## Integration Points
This file integrates NameNode fsimage save/load, protobuf image sections, XML writer/reconstructor, WebHDFS-compatible read-only WebImageViewer operations, delimited text export, parallel processor behavior, EC policy metadata, xattrs/ACLs/snapshots/delegation-token sections, and corruption detector output.

## Risks
The test is large and stateful; many assertions depend on hard-coded inode IDs, generated namespace order, expected resource CSVs, and default timezone. Static `dirCount` and `writtenFiles` can accumulate if setup is rerun in the same JVM unexpectedly. Some tests use `db != ""` identity comparison for strings, which works for current literals but is fragile style. WebImageViewer tests depend on ephemeral HTTP ports and WebHDFS client behavior.

## Test Signals
Signals include processor return codes, file/directory counts, max file size, valid XML parsing, WebHDFS status equality, HTTP error codes, delimited field counts and path set equality, matching MD5 for serial/parallel delimited output, exact corruption CSV outputs, XML round-trip diffs being empty, layout-version mismatch failure, and EC policy XML fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForAcl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForAcl.java

## Purpose
`TestOfflineImageViewerForAcl` validates OIV handling of fsimages containing HDFS ACL metadata through WebImageViewer, XML writer, and delimited writer.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `AclStatus`, `AclTestHelpers.aclEntry`, `PBImageXmlWriter`, `PBImageDelimitedTextWriter`, and secure SAX parser helpers.

## Control Flow
`createOriginalFSImage()` enables ACLs, creates directories/files with no ACLs, default ACLs, access ACLs, and multiple named ACL entries, stores expected `AclStatus` objects, saves namespace, and records the fsimage. Tests start WebImageViewer and compare `GETACLSTATUS` through WebHDFS for each path, verify invalid-path HTTP 404, parse XML output for well-formedness, and inspect delimited permissions for the ACL `+` suffix.

## State, Persistence, And Dependencies
Static state includes the generated fsimage and a map of expected ACL statuses. The fsimage is deleted in `AfterAll`.

## Integration Points
This tests ACL persistence from NameNode metadata into fsimage, OIV XML export, OIV delimited permission formatting, and WebImageViewer's WebHDFS ACL endpoint.

## Risks
The delimited writer test infers ACL presence from whether the path name contains "noacl", which is compact but naming-sensitive. XML test checks parseability rather than exact ACL contents. WebHDFS status equality depends on `AclStatus.equals` semantics.

## Test Signals
Signals include exact `AclStatus` equality, HTTP 404 for invalid ACL path, successful SAX parsing, and ACL-mark suffixes in delimited permission fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForContentSummary.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForContentSummary.java

## Purpose
`TestOfflineImageViewerForContentSummary` verifies WebImageViewer `GETCONTENTSUMMARY` behavior for directories, empty directories, files, symlinks, directories containing symlinks, quotas, and missing paths.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `ContentSummary`, `SafeModeAction`, and HTTP connections.

## Control Flow
`createOriginalFSImage()` creates a parent directory with child directories and files, sets namespace/storage quotas, records `ContentSummary` values directly from DFS for representative paths, creates symlinks to a file and directory, saves namespace, and records the fsimage. Each test starts a WebImageViewer, checks HTTP OK for a path where applicable, obtains content summary via WebHDFS, and compares selected counters with the saved DFS summary. One test verifies missing path returns HTTP 404.

## State, Persistence, And Dependencies
Static state consists of the generated fsimage and expected `ContentSummary` instances. The cluster is shut down after image generation; tests are read-only against the image.

## Integration Points
This maps NameNode content summary semantics into WebImageViewer's read-only WebHDFS API and validates quota and symlink accounting.

## Risks
The expected symlink behavior is whatever DFS returned at image-generation time, so semantic changes in symlink content summaries can require updating both production and test assumptions. Each test starts its own HTTP server, so port setup and teardown must be reliable.

## Test Signals
Signals include HTTP OK/NOT_FOUND codes and equality of directory count, file count, length, space consumed, namespace quota, and space quota.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForContentSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForErasureCodingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForErasureCodingPolicy.java

## Purpose
`TestOfflineImageViewerForErasureCodingPolicy` validates delimited OIV output for inherited and explicit erasure coding policy metadata.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `OfflineImageViewerPB`, `DFSTestUtil.readResoucePlainFile`, and the delimited writer `-ec` option.

## Control Flow
Image setup starts a 10-DataNode cluster, enables RS-6-3 and RS-3-2 policies, creates directories with EC policies plus nested subdirectories/files, creates a replicated directory tree, saves namespace, and records the fsimage. The test runs OIV with `-p Delimited -ec`, reads the output file, extracts path and field 12 EC policy values, and compares the path-policy CSV against `testErasureCodingPolicy.csv`.

## State, Persistence, And Dependencies
State is the generated fsimage, temp NameNode directory, and delimited output file. Expected output is a checked-in resource.

## Integration Points
This checks NameNode EC policy inheritance as represented in fsimage and emitted by OIV's delimited exporter.

## Risks
Expected resource output is sensitive to traversal order and policy display strings. The local variable `delemiter` is misspelled but harmless. The test assumes the EC policies exist with exact names.

## Test Signals
The main signal is exact equality between extracted path/policy lines and the resource file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForErasureCodingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForStoragePolicy.java

## Purpose
`TestOfflineImageViewerForStoragePolicy` validates delimited OIV output for storage policy IDs on files and directories.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `OfflineImageViewerPB`, `HdfsConstants` storage policy names, and `DFSTestUtil.readResoucePlainFile`.

## Control Flow
Setup enables storage policy support, creates directory trees with unspecified, ALLSSD, and HOT policies, creates files with and without ALLSSD, saves namespace, and records the fsimage. The test runs OIV Delimited with `-sp`, reads field 12 as a storage-policy integer for each non-header row, and compares generated path,id lines against `testStoragePolicy.csv`.

## State, Persistence, And Dependencies
State includes the generated fsimage, temp directory, and delimited output file. Expected output is a checked-in resource.

## Integration Points
This validates fsimage storage policy metadata and the `PBImageDelimitedTextWriter` storage-policy column.

## Risks
It depends on numeric storage policy IDs, which are more brittle than names if policy definitions change. The `ByteArrayOutputStream output` variable is unused. Traversal ordering must match the resource file.

## Test Signals
The signal is exact equality between extracted path/storage-policy-id CSV and the expected resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForXAttr.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForXAttr.java

## Purpose
`TestOfflineImageViewerForXAttr` verifies WebImageViewer support for listing and retrieving xattrs from fsimage metadata.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `XAttrHelper`, `JsonUtil`, HTTP connections, and Apache Commons IO stream reading.

## Control Flow
Setup creates `/dir1` with two user xattrs, saves namespace, precomputes expected JSON for `user.attr1`, and records the fsimage. Tests start WebImageViewer and call HTTP endpoints for `LISTXATTRS`, `GETXATTRS` with no parameters, invalid xattr parameter, valid parameter, uppercase name with `encoding=TEXT`, and missing xattr. One test uses `WebHdfsFileSystem` APIs to list names, get one xattr, get uppercase-name xattr, and get a map for both names.

## State, Persistence, And Dependencies
State is the generated fsimage and expected JSON string. All endpoint tests are read-only.

## Integration Points
This checks fsimage xattr persistence through WebImageViewer's WebHDFS-compatible HTTP surface and WebHDFS client wrappers.

## Risks
The test expects case-insensitive handling for xattr namespace/name in at least some paths. JSON equality is exact for selected xattr output. HTTP response-code semantics distinguish bad request for malformed names and forbidden for absent attributes, so behavior changes may need careful compatibility review.

## Test Signals
Signals include HTTP OK/BAD_REQUEST/FORBIDDEN codes, response bodies containing both xattr names, exact JSON for a selected xattr, WebHDFS API name/value equality, and map values for both attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForXAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerWithStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerWithStripedBlocks.java

## Purpose
`TestOfflineImageViewerWithStripedBlocks` verifies that OIV/FSImageLoader reports correct file lengths for erasure-coded striped files across stripe and block-group boundary sizes.

## Important APIs, Types, And Functions
It uses `StripedFileTestUtil`, `ErasureCodingPolicy`, `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `FSImageLoader`, `FSDirectory`, `INodeFile`, `BlockInfo`, and `BlockInfoStriped`.

## Control Flow
Setup starts a cluster with enough DataNodes for data plus parity plus spare nodes, sets block size to three EC cells, enables the default EC policy, and creates `/eczone`. Seven tests call `testFileSize` with sizes less than a stripe, equal to one stripe, multiple blocks, full block group, and over block-group boundaries. The helper writes sequential bytes, saves namespace, loads the image, gets JSON file status, and compares both in-memory `BlockInfoStriped` byte sums and JSON `"length"` against expected bytes length.

## State, Persistence, And Dependencies
State includes a cluster per test, EC policy metadata, the striped file, saved fsimage, and NameNode FSDirectory. The cluster is shut down in teardown.

## Integration Points
This links EC striped block metadata in NameNode, fsimage save/load, `FSImageLoader.getFileStatus`, and JSON status serialization.

## Risks
The test assumes `/` EC policy setting plus `/eczone` creation yields striped files for created paths. It uses live NameNode `FSDirectory` after saving namespace to validate block internals, so failures can reflect either writer or loader behavior. File paths are reused across tests but each test gets a fresh cluster.

## Test Signals
Signals include correct EC policy ID on the inode, all blocks being `BlockInfoStriped`, summed block bytes equaling written byte length, and OIV JSON file status containing the expected `"length"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerWithStripedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestPBImageCorruption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestPBImageCorruption.java

## Purpose
`TestPBImageCorruption` unit-tests `PBImageCorruption` classification and mutation behavior.

## Important APIs, Types, And Functions
The only production type under test is `PBImageCorruption`, with methods `getType`, `getId`, `getNumOfCorruptChildren`, `addMissingChildCorruption`, `addCorruptNodeCorruption`, and `setNumberOfCorruption`.

## Control Flow
One test constructs a corrupt-node instance, adds missing-child corruption, and checks the combined type. Another verifies that constructing an instance with neither corruption kind throws `IllegalArgumentException`. The last test starts from a missing-child instance, validates ID/type/count, adds corrupt-node corruption, updates count, and checks combined type/count.

## State, Persistence, And Dependencies
State is entirely in-memory object fields. There is no filesystem or cluster dependency.

## Integration Points
This supports the larger PB image corruption detector tests by pinning the value-object semantics used in detector output.

## Risks
Coverage is intentionally narrow and does not test CSV rendering or detector traversal. Type strings are exact and user-visible to corruption reports.

## Test Signals
Signals are exact type strings, ID and count getters, count mutation, and constructor validation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestPBImageCorruption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/HostsFileWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/HostsFileWriter.java

## Purpose
`HostsFileWriter` is a test utility for creating and updating HDFS include/exclude host files in both legacy split-file format and combined host-file format.

## Important APIs, Types, And Functions
It uses local `FileSystem`, `MiniDFSCluster.getBaseDirectory`, `DFSTestUtil.writeFile`, `CombinedHostsFileWriter`, `DatanodeAdminProperties`, `HostFileManager`, `HostConfigManager`, and DFS host config keys. Public methods include `initialize`, `initExcludeHost(s)`, `initOutOfServiceHosts`, `initIncludeHost(s)`, `initIncludeHosts(DatanodeAdminProperties[])`, `cleanup`, `getIncludeFile`, and `getExcludeFile`.

## Control Flow
`initialize` sets up a local directory, deletes leftovers, decides whether the configured provider is legacy `HostFileManager`, and either creates separate `include`/`exclude` files or a combined `all` file while updating configuration keys. Include/exclude methods write line-oriented legacy files or construct `DatanodeAdminProperties` sets for combined JSON-like output. Maintenance state is only supported in combined mode.

## State, Persistence, And Dependencies
State includes local paths, local filesystem handle, provider mode flag, and generated host files under the MiniDFSCluster base directory. `cleanup` deletes the whole utility directory with `FileUtils.deleteQuietly`.

## Integration Points
The utility feeds NameNode include/exclude host provider tests, decommission tests, maintenance-state tests, and `GetConf` include/exclude command tests.

## Risks
`cleanup()` assumes `localFileSys` and `fullDir` have been initialized; calling it earlier would fail. Combined-mode parsing assumes `host:port` and validates decommission entries more strictly than maintenance/include entries. The legacy path rejects maintenance with `UnsupportedOperationException`.

## Test Signals
As a helper, its signals are indirect: generated config keys point to existing files, legacy files contain expected host lines, combined files contain expected `DatanodeAdminProperties`, and callers can inspect include/exclude paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/HostsFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestAtomicFileOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestAtomicFileOutputStream.java

## Purpose
`TestAtomicFileOutputStream` verifies atomic write/replace semantics and cleanup behavior for `AtomicFileOutputStream`.

## Important APIs, Types, And Functions
It uses `AtomicFileOutputStream`, `DFSTestUtil.readFile`, `FileUtil`, `PathUtils`, `IOUtils`, and `PlatformAssumptions.assumeWindows`. `createFailingStream()` subclasses `AtomicFileOutputStream` to inject a `flush()` failure.

## Control Flow
Before each test, the test directory is created and emptied. `testWriteNewFile` writes to a non-existing destination and confirms the destination appears only after close. `testOverwriteFile` confirms existing destination contents remain unchanged until close, then are replaced. `testFailToFlush` injects close-time flush failure and checks the original file remains intact and the temp file is removed. `testFailToRename` runs only on Windows, makes the directory non-writable, closes the stream, and expects a native rename failure.

## State, Persistence, And Dependencies
State is local filesystem content under the test directory, including destination and temporary files. Tests mutate directory writability on Windows and restore it in finally.

## Integration Points
This tests the local durable-write primitive used by HDFS utilities for atomic file replacement.

## Risks
Rename and writability behavior is platform-specific; the Windows-only test is guarded but still depends on native error wording. Failure injection only covers `flush()`, not all possible write or close failures. Directory listing assertion assumes only destination remains after cleanup.

## Test Signals
Signals include destination existence before/after close, exact file contents before/after close, thrown `IOException` on injected failure, temp-file cleanup via directory listing, and Windows rename error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestAtomicFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestBestEffortLongFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestBestEffortLongFile.java

## Purpose
`TestBestEffortLongFile` verifies best-effort persistence of a single long value and default handling for absent or truncated files.

## Important APIs, Types, And Functions
It uses `BestEffortLongFile`, `MiniDFSCluster.getBaseDirectory`, `IOUtils.closeStream`, `Random`, and JUnit assertions.

## Control Flow
`cleanup()` removes the test file before each test and ensures the parent directory exists. `testGetSet` creates a `BestEffortLongFile` with default `12345`, verifies `get()` returns the default and creates the file, then writes 100 random long values, checking each through the same instance and a newly opened instance. `testTruncatedFileReturnsDefault` creates an empty file and verifies `get()` falls back to the configured default.

## State, Persistence, And Dependencies
State is a local file under the MiniDFSCluster base directory. The test explicitly checks persistence across new `BestEffortLongFile` instances and closes instances with `IOUtils` or direct close.

## Integration Points
This covers a small persistence utility used where HDFS wants durable-ish scalar state without hard failure on missing/corrupt local files.

## Risks
Random values provide breadth but no deterministic seed for reproducing a specific value, though failures would generally be value-independent. It does not cover partial nonzero files, permission failures, or concurrent access.

## Test Signals
Signals include default value on absent/truncated file, file creation after first access, same-instance reads after `set`, and cross-instance reads proving data was written.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestBestEffortLongFile.java -->
