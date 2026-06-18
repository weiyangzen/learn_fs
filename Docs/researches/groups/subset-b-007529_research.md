# Research: subset-b-007529

Grouped research for HDFS test sources under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatus.java

## Purpose
JUnit coverage for HDFS `FileStatus`, `HdfsFileStatus`, `FileContext.listStatus`, `FileSystem.listStatus`, and list iterators. It validates file, directory, nonexistent-path, qualification, content-summary length, listing order, and erasure-coding status for non-EC paths.

## APIs and Control Flow
`@BeforeAll testSetUp` builds a `MiniDFSCluster`, sets `DFS_LIST_LIMIT` to 2 to force batched listings, initializes `FileSystem`, `FileContext`, `DFSClient`, and creates `filestatus.dat`. `testGetFileInfo` checks root, null return for missing `DFSClient.getFileInfo`, child counts, and non-absolute path rejection. `testGetFileStatusOnFile`, `testListStatusOnFile`, `testGetFileStatusOnNonExistantFileDir`, and `testGetFileStatusOnDir` exercise direct status calls, one-file listing, missing-path exception messages, and increasingly populated directory iteration, including deletion while iterating.

## State, Dependencies, Integration
State is cluster-local namespace metadata and file blocks. It depends on `DFSTestUtil`, `ContractTestUtils`, `GenericTestUtils`, `FSNamesystem`, and both old and newer status iterator APIs. It integrates client-side `DFSClient` semantics with public `FileSystem` and `FileContext` behavior.

## Risks and Test Signals
Strong signals are exact assertions on block size, replication, lengths, qualified paths, EC flags, iterator ordering, and `FileNotFoundException` behavior. Risk areas are brittle exception text, ordering assumptions from HDFS directory listing, and races around deleting a parent while a batched iterator is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusSerialization.java

## Purpose
Verifies compatible serialization between `HdfsFileStatus`, `FileStatus`, HDFS protobuf status, generic FS protobuf status, Java serialization, and Writable serialization, with special attention to 2.x `FsPermission` flag compatibility.

## APIs and Control Flow
`baseStatus()` builds an `HdfsFileStatusProto` with file metadata, permissions, owner/group, times, replication, block size, and flags. `checkFields` compares core `FileStatus` properties. `testFsPermissionCompatibility` iterates legacy-compatible flag values, converts through `PBHelperClient`, qualifies paths, checks ACL/encryption/EC bits, writes via `DataOutputBuffer`, reads via `DataInputBuffer`, and verifies flag preservation. `testJavaSerialization` round-trips an `HdfsFileStatus` through `ObjectOutputStream/ObjectInputStream`. `testCrossSerializationProto` serializes each HDFS file type into `FileStatusProto`, checks aligned fields, and parses back to ensure unknown fields survive.

## State, Dependencies, Integration
The test is pure serialization state with no cluster. It depends on protobuf classes, `PBHelperClient`, `DataInputBuffer`, `DataOutputBuffer`, `FsPermission`, and Java object serialization. It integrates HDFS-specific file status wire compatibility with the common FS status schema.

## Risks and Test Signals
High-value signals are byte-level proto round trips and permission-extension bit checks. Risks are ordinal coupling between proto enum values, deprecated permission extension behavior, and accidental loss of unknown fields during schema evolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithDefaultECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithDefaultECPolicy.java

## Purpose
Tests that HDFS file status and client file info correctly report erasure-coding policy state for directories and files when the default system EC policy is used.

## APIs and Control Flow
`before` creates a one-DN `MiniDFSCluster`, obtains `DistributedFileSystem` and `DFSClient`, and enables `getEcPolicy()`. `getEcPolicy` returns `StripedFileTestUtil.getDefaultECPolicy`. `testFileStatusWithECPolicy` creates `/foo`, verifies no EC policy initially on directory or file, sets the EC policy on the directory, verifies the directory policy through `DFSClient.getFileInfo`, creates a child file, and checks inherited EC status through `FileStatus`, `HdfsFileStatus`, and `ContractTestUtils`.

## State, Dependencies, Integration
State is namespace metadata for EC policy inheritance. It depends on `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `ErasureCodingPolicy`, `FsPermission`, and `ContractTestUtils`. It integrates EC policy management with status reporting and string rendering.

## Risks and Test Signals
Signals include explicit null/non-null policy checks and `FileStatus#toString` containing `isErasureCoded=true`. Risks are running a striped-policy test on a one-DN cluster where policy metadata is tested but full striped IO is not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithDefaultECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithRandomECPolicy.java

## Purpose
Reuses the default EC file-status test with a random non-default erasure-coding policy, broadening coverage beyond the default policy.

## APIs and Control Flow
The class extends `TestFileStatusWithDefaultECPolicy`, chooses `StripedFileTestUtil.getRandomNonDefaultECPolicy()` in the constructor, logs the selected policy, and overrides `getEcPolicy()` to return that policy. All inherited setup and assertions run against the selected non-default policy.

## State, Dependencies, Integration
State is inherited cluster and namespace metadata from the superclass plus the per-instance `ErasureCodingPolicy`. It depends on `StripedFileTestUtil` and SLF4J logging. It integrates random EC policy selection with the same status-reporting API contract.

## Risks and Test Signals
The inherited assertions remain the main signal. The main risk is nondeterminism: failures may depend on the randomly selected policy unless logs are preserved. The test does not add new methods, so inherited lifecycle assumptions must remain compatible with all non-default policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFsShellPermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFsShellPermission.java

## Purpose
Tests privilege and permission behavior of `FsShell -rm -r` and `-rm -r -f` against HDFS directories and files owned by different users.

## APIs and Control Flow
`FileEntry` describes test paths, directory flags, owners, groups, and permissions. `createFiles` materializes those entries, sets permission and owner, and `deldir` cleans test roots. `execCmd` captures `FsShell.run` output and return code. `TestDeleteHelper.execute` builds a fixture under `/testroot`, runs the shell command under a chosen `UserGroupInformation`, then verifies whether the target was deleted. Helper factories create empty-directory, non-empty-directory, and single-file cases with varying target permissions and user identities. `testDelete` creates a `MiniDFSCluster`, builds the helper list, and executes each scenario.

## State, Dependencies, Integration
State is HDFS ownership, group, permissions, and delete side effects. It depends on `FsShell`, `FileSystemTestHelper`, `UserGroupInformation`, `FsPermission`, and Apache `StringUtils`. It integrates CLI behavior with Namenode permission enforcement.

## Risks and Test Signals
The signal is binary existence after command execution for each permission matrix entry. Risks include captured `System.out` global mutation, command parsing by whitespace, and permission semantics that depend on parent directory permissions more than child readability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFsShellPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetBlocks.java

## Purpose
Slow integration tests for block-location and balancer-oriented `NamenodeProtocol.getBlocks` behavior, including stale nodes, min block size, safe mode rejection, hot-block ordering, stale storage exclusion, and storage-type filtering.

## APIs and Control Flow
`testReadSelectNonStaleDatanode` writes an unclosed file, marks selected DNs stale by disabling heartbeats and manipulating last-update timestamps, then checks stale replicas move to the end of read locations. `testGetBlocks` creates a 13-block file, calls `getBlocks` with different sizes and min-block sizes, validates storage IDs, invalid arguments, nonexistent DN errors, `testBlockIterator`, and safe-mode failure. `testBlockKey` checks block hash/equality using grandfather generation stamps. `testGetBlocksWithHotBlockTimeInterval` verifies older file blocks are preferred before new ones. `testReadSkipStaleStorage` marks individual storage stale and all storages stale. `testChooseSpecifyStorageType` creates SSD and DISK files through storage policies and filters `getBlocks` by `StorageType`.

## State, Dependencies, Integration
State spans block maps, DN descriptors, storage infos, safe mode, heartbeat freshness, storage policies, and block locations. Dependencies include `MiniDFSCluster`, `DFSClient`, `NamenodeProtocol`, `BlockManagerTestUtil`, `DataNodeTestUtils`, `DFSTestUtil`, and `NameNodeProxies`. It directly integrates client reads, block-manager internals, balancer RPCs, and storage policy placement.

## Risks and Test Signals
Signals are exact block counts, exception classes/messages, ordering assertions, storage IDs/types, and iterator immutability checks. Risks are timing-sensitive stale-node simulation, safe-mode state cleanup, random block-key seed reproducibility only via stdout, and dependence on internal block/storage iteration order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetFileChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetFileChecksum.java

## Purpose
Validates HDFS file checksum semantics for appended files and rejects checksums for files with blocks under construction.

## APIs and Control Flow
`setUp` builds a three-DN cluster with 1024-byte blocks. `testGetFileChecksum(Path,int)` creates a file, records the full checksum after each of 16 append rounds, then calls `getFileChecksum(path, prefixLength)` and verifies each prefix checksum matches the earlier whole-file checksum at that length. `testGetFileChecksumForBlocksUnderConstruction` writes to an unclosed stream and expects `getFileChecksum` to fail with an under-construction message. `testGetFileChecksum` runs aligned and unaligned append lengths.

## State, Dependencies, Integration
State is block checksum metadata across appends and open-file construction state. Dependencies include `DFSTestUtil`, `FileChecksum`, `FSDataOutputStream`, and `DistributedFileSystem`. It integrates append, checksum prefix API, and open-block validation.

## Risks and Test Signals
Signals are checksum equality across append history and explicit IOException message content. Risks include brittle message text and possible timing around open stream visibility, though the under-construction stream is deliberately left open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetFileChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHAAuxiliaryPort.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHAAuxiliaryPort.java

## Purpose
Tests HA NameNode auxiliary RPC ports and verifies the same namespace operations work through main and auxiliary ports before and after failover.

## APIs and Control Flow
The test configures two auxiliary RPC ports globally and per HA NN, defines a two-NameNode topology, builds a zero-DN HA `MiniDFSCluster`, transitions NN0 active, obtains both `NameNodeRpcServer` instances and their auxiliary addresses, creates `/test` via NN0 main RPC URI, verifies existence through NN0 auxiliary ports, shuts down NN0, transitions NN1 active, and verifies existence through NN1 main and auxiliary ports.

## State, Dependencies, Integration
State is HA namespace metadata and per-NameNode RPC listener sets. Dependencies include `MiniDFSNNTopology`, `NameNodeRpcServer`, `DFSClient`, HA config keys, and URI-based client construction. It integrates failover with multi-listener RPC access.

## Risks and Test Signals
Signals are auxiliary address counts and cross-port `exists` checks. Risks include fixed configured auxiliary ports (`9000,9001`) colliding on shared hosts and a minor assertion bug in the NN1 auxiliary loop that calls `client1.exists` instead of `clientTmp.exists`, reducing direct coverage of those auxiliary clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHAAuxiliaryPort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSFileSystemContract.java

## Purpose
Runs generic `FileSystemContractBaseTest` coverage against HDFS and adds HDFS-specific append and path-capability checks.

## APIs and Control Flow
`setUp` creates a two-DN `MiniDFSCluster` under a randomized test directory and applies the contract-test umask. `getDefaultWorkingDirectory` returns `/user/<shortUser>`, and `getGlobalTimeout` sets 60 seconds. `testAppend` delegates to `AppendTestUtil.testAppend`. `testFileSystemCapabilities` verifies `DistributedFileSystem` advertises `LEASE_RECOVERABLE` and implements `LeaseRecoverable` and `SafeMode`.

## State, Dependencies, Integration
State is generic filesystem namespace and append data in a mini cluster. Dependencies include `FileSystemContractBaseTest`, `AppendTestUtil`, `CommonPathCapabilities`, AssertJ, and HDFS cluster setup. It integrates public HDFS FS behavior with the common Hadoop FS contract suite.

## Risks and Test Signals
Signals are inherited contract tests plus explicit append and capability assertions. Risks are that capability checks are conditional on `DistributedFileSystem`, so alternate FS wrappers skip them; generic inherited coverage depends on superclass behavior not visible in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSPolicyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSPolicyProvider.java

## Purpose
Ensures `HDFSPolicyProvider` declares service ACL policies for every RPC protocol implemented by important HDFS RPC server classes.

## APIs and Control Flow
`initialize` loads all `Service` entries from `HDFSPolicyProvider` into `policyProviderProtocols`. `data` parameterizes the test over `NameNodeRpcServer`, `DataNode`, and `JournalNodeRpcServer`. `testPolicyProviderForServer` uses `ClassUtils.getAllInterfaces`, filters interfaces whose names end with `Protocol`, and checks the set difference from policy-provider protocols is empty.

## State, Dependencies, Integration
State is static reflection-derived sets of protocol classes. Dependencies include `HDFSPolicyProvider`, `Service`, HDFS server classes, `ClassUtils`, JUnit parameterization, and `Sets.difference`. It integrates service authorization configuration with actual RPC surface area.

## Risks and Test Signals
The key signal is a failing diff listing uncovered protocols. Risks are naming-convention dependence (`endsWith("Protocol")`), reflection including inherited interfaces that may not require policy, and missing protocols whose interface names do not follow the convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSServerPorts.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSServerPorts.java

## Purpose
Tests port binding behavior for NameNode, DataNode, SecondaryNameNode, and BackupNode: fixed occupied ports should fail with bind errors, while free or ephemeral ports should allow startup.

## APIs and Control Flow
`getFullHostName` chooses a host address, `startNameNode` formats and starts a NameNode with RPC/HTTP and optional service RPC addresses, `startBackupNode` creates backup storage dirs and starts a backup NameNode, and `startDataNode` creates a DN data dir. `canStartNameNode`, `canStartDataNode`, `canStartSecondaryNode`, and `canStartBackupNode` attempt startup and return false on `BindException`. Tests then occupy ports with running services and verify conflicting and non-conflicting startup cases.

## State, Dependencies, Integration
State is local filesystem storage dirs, process-local metrics system mini-cluster mode, and bound sockets. Dependencies include `NameNode`, `DataNode`, `BackupNode`, `SecondaryNameNode`, `FileUtil`, `DFSTestUtil`, `DNS`, and `PathUtils`. It integrates HDFS daemon config keys with runtime port binding behavior.

## Risks and Test Signals
Signals are boolean startup results for each daemon. Risks include host DNS differences, OS-specific port release timing, shared test-machine port conflicts, and reliance on daemon constructors mutating `Configuration` with actual bound ports. The file should remain sensitive to brace placement around helper methods; the checked content has `canStartBackupNode` correctly inside the class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSServerPorts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSTrash.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSTrash.java

## Purpose
Tests Trash behavior on HDFS, including shell trash operations, non-default FS configuration, permissions, empty directory moves, deleting trash directories, and duplicate inode names in trash paths.

## APIs and Control Flow
`setUp` creates a two-DN cluster, initializes world-writable test and trash roots, and creates test users. Simple tests delegate to `TestTrash` helpers. `testDeleteTrash` logs in as user1 and user2, moves per-user temp dirs to isolated trash roots, verifies a user can delete own trash and cannot delete another user's trash, checking the denied message includes the username. `getPerUserTrash` uses a Mockito spy to override `FileSystem.getTrashRoot`. `testDeleteToTrashWhenInodeNameDuplicate` moves a file and a nested directory with duplicate path component names into trash.

## State, Dependencies, Integration
State includes HDFS permissions, trash roots, user identities, and moved namespace entries. Dependencies include `Trash`, `TestTrash`, `DFSTestUtil.login`, `UserGroupInformation`, `FsPermission`, `FsAction`, `AccessControlException`, and Mockito. It integrates public trash APIs with HDFS permission enforcement.

## Risks and Test Signals
Signals are successful delegated helper checks, existence/deletion assertions, and denied access containing the username. Risks include static `fs` being reassigned across tests, mocked trash-root behavior masking real root selection, and test isolation relying on unique UUID trash paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSTrash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHFlush.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHFlush.java

## Purpose
Tests HDFS `hflush` and `hsync` semantics across normal writes, custom checksum/block boundaries, `SyncFlag.UPDATE_LENGTH`, `SyncFlag.END_BLOCK`, pipeline heartbeat delays, and interrupted flush/close behavior.

## APIs and Control Flow
Small test methods call `doTheJob` with combinations of block size, checksum size, replicas, `hflush` vs `hsync`, and sync flags. `hSyncUpdateLength_00` verifies zero-byte `hsync(UPDATE_LENGTH)` keeps length zero. `hSyncEndBlock_00` checks `END_BLOCK` on empty and partial blocks, block counts, and visible lengths. `doTheJob` creates a cluster, writes ten sections of `AppendTestUtil.FILE_SIZE`, flushes or syncs after each section, optionally validates visible length or located block count, reads back each section through a fresh input stream, then checks the full file. `testPipelineHeartbeat` writes slowly across socket-timeout intervals. `testHFlushInterrupted` verifies interrupt status and `InterruptedIOException` behavior around `hflush` and `close`.

## State, Dependencies, Integration
State includes output pipeline packets, block boundaries, visible file length, located blocks, and thread interrupted status. Dependencies include `DFSOutputStream`, `HdfsDataOutputStream.SyncFlag`, `LocatedBlocks`, `AppendTestUtil`, and `MiniDFSCluster`. It integrates low-level DFS client stream behavior with public `FSDataOutputStream`.

## Risks and Test Signals
Signals are byte-accurate reads, file length checks, located-block counts, full-file validation, and interrupt-status assertions. Risks include timing-sensitive heartbeat sleeps, duplicate `@Test` annotation on `hSyncEndBlock_02` being harmless but noisy, and reliance on internal `DFSOutputStream` casting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHFlush.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHdfsAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHdfsAdmin.java

## Purpose
Tests `HdfsAdmin` administration APIs for quotas, URI validation, storage policies, key-provider discovery, and paginated listing of open files.

## APIs and Control Flow
`setUpCluster` sets the open-files response batch size and starts a two-DN cluster. `testHdfsAdminSetQuota` sets and clears namespace and space quotas, checking content summaries after each operation. `testHdfsAdminWithBadUri` verifies non-HDFS URI rejection. `testHdfsAdminStoragePolicies` creates nested files, sets WARM/COLD/HOT policies, unsets them, and compares all policy names with `BlockStoragePolicySuite`. `testGetKeyProvider` checks null provider on a normal cluster, restarts with a JKS key provider path, and expects non-null. `testListOpenFiles` creates closed and open files in batches and repeatedly verifies old and new `listOpenFiles` APIs omit closed files and include all open files.

## State, Dependencies, Integration
State includes quotas, block storage policy metadata, key-provider config, open output streams, and Namenode open-file iteration. Dependencies include `HdfsAdmin`, `BlockStoragePolicySuite`, `JavaKeyStoreProvider`, `OpenFilesIterator`, `DFSTestUtil`, and `RemoteIterator`. It integrates admin client APIs with Namenode metadata operations.

## Risks and Test Signals
Signals are exact quota values, policy equality, provider nullability, and set-based open-file reconciliation. Risks include leaking open streams if a failure interrupts cleanup, batch-size sensitivity, and provider-path filesystem cleanup through `FileSystemTestHelper`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHdfsAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHttpPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHttpPolicy.java

## Purpose
Verifies invalid HDFS HTTP policy configuration is rejected with `HadoopIllegalArgumentException`.

## APIs and Control Flow
`testInvalidPolicyValue` creates a `Configuration`, sets `DFS_HTTP_POLICY_KEY` to `"invalid"`, and asserts `DFSUtil.getHttpPolicy(conf)` throws `HadoopIllegalArgumentException`.

## State, Dependencies, Integration
The only state is configuration key/value data. Dependencies are `Configuration`, `DFSConfigKeys`, `DFSUtil`, and JUnit `assertThrows`. It integrates config parsing with validation of the HTTP/HTTPS policy enum contract.

## Risks and Test Signals
The signal is direct exception type matching. Risk is narrow coverage: it does not check accepted values or exception messages, only the invalid-value failure path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHttpPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestInjectionForSimulatedStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestInjectionForSimulatedStorage.java

## Purpose
Tests simulated-storage block injection and replication recovery: after simulated DNs lose block contents across restart, injected blocks on one DN should seed replication back to the configured factor.

## APIs and Control Flow
`waitForBlockReplication` polls `ClientProtocol.getBlockLocations` until each expected block has the requested number of locations. `testInjection` configures `SimulatedFSDataset`, creates a four-block file with replication 4, records all block reports, shuts down the cluster, restarts without formatting with twice as many simulated DNs and safemode threshold 0, extracts unique blocks from old reports, injects them into DN0 via `cluster.injectBlocks`, and waits for replication back to four replicas.

## State, Dependencies, Integration
State includes Namenode namespace persistence, simulated DN block reports, injected block lists, and replication queues. Dependencies include `SimulatedFSDataset`, `BlockListAsLongs`, `DatanodeStorage`, `DFSClient`, `MiniDFSCluster`, and `Time`. It integrates test-only simulated storage with block-manager replication scheduling.

## Risks and Test Signals
Signals are block count and per-block replica count convergence. Risks include unbounded wait when `maxWaitSec` is negative, simulated storage diverging from real disk behavior, and restart-without-format relying on preserved test storage dirs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestInjectionForSimulatedStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestIsMethodSupported.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestIsMethodSupported.java

## Purpose
Verifies client-side protobuf translators and protocol proxies correctly implement `isMethodSupported` for NameNode, DataNode, Journal, inter-DN, refresh, and user-mapping protocols.

## APIs and Control Flow
`setUp` starts a one-DN cluster and records NN and DN IPC addresses. Each test constructs the relevant protocol proxy or translator and checks a known supported or unsupported method: `rollEditLog`, `sendHeartbeat`, `refreshNamenodes`, `mkdirs`, `startLogSegment`, `initReplicaRecovery`, `getGroupsForUser`, `refreshServiceAcl`, `refreshUserToGroupsMappings`, and `refreshCallQueue`.

## State, Dependencies, Integration
State is live RPC servers and negotiated protocol metadata. Dependencies include `RpcClientUtil`, `RPC`, `NameNodeProxies`, PB translator classes, `NetUtils`, `UserGroupInformation`, and security/admin protocols. It integrates protocol meta-interface behavior across HDFS and common Hadoop RPC surfaces.

## Risks and Test Signals
Signals are true/false support checks at correct endpoints. Risks include endpoint mix-ups, method-name string brittleness, and `testClientNamenodeProtocol` not asserting the returned boolean even though it performs the lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestIsMethodSupported.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestKeyProviderCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestKeyProviderCache.java

## Purpose
Tests `KeyProviderCache` identity caching and invalidation behavior for configured key-provider URIs.

## APIs and Control Flow
`DummyKeyProvider` implements the abstract `KeyProvider` methods as no-ops and increments a static close counter. `Factory` creates dummy providers for `dummy://` URIs. `testCache` creates a cache, requests providers for identical URI, different host URI, and same host with different userinfo, checking object identity differences, then calls `invalidateCache` and expects three close calls. `getKeyProviderUriFromConf` reads the configured provider path and converts it to `URI`.

## State, Dependencies, Integration
State is cache contents keyed by provider URI and static close-call count. Dependencies include Hadoop crypto `KeyProvider`, `KeyProviderFactory`, `CommonConfigurationKeysPublic`, and URI parsing. It integrates cache lifetime behavior with provider factory resolution.

## Risks and Test Signals
Signals are identity equality/inequality and close count. Risks include static `CLOSE_CALL_COUNT` not reset between repeated runs in the same JVM and needing service-provider registration for `Factory` outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestKeyProviderCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLargeBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLargeBlock.java

## Purpose
Tests HDFS can write, close, read, and report file length for a block larger than 2 GB.

## APIs and Control Flow
`createFile` opens an `FSDataOutputStream` with a caller-supplied block size. `writeFile` writes a repeating `DEADBEEF` pattern in 64 MiB chunks until the requested file size is reached. `checkFullFile` reads in 128 MiB chunks and compares against the expected pattern. `testLargeBlockSize` sets block size to 2 GiB + 512 bytes and delegates to `runTest`. `runTest` creates a three-DN cluster, writes a file of blockSize + 1, closes it, reads it back, and checks `FileStatus.getLen`.

## State, Dependencies, Integration
State is large file block metadata and block data in a mini cluster. Dependencies include `MiniDFSCluster`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `CommonConfigurationKeys`, and JUnit timeout. It integrates client IO buffering with large block metadata boundaries beyond 32-bit sizes.

## Risks and Test Signals
Signals are full-pattern verification and exact file length. Risks are high runtime, disk/memory pressure from multi-GiB IO, and a 30-minute timeout that may still be environment-sensitive, especially on slower filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLargeBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLease.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLease.java

## Purpose
Tests HDFS client lease lifecycle, lease-renewal failure handling, lease movement across renames, file recreation after rename, delete/open-file validation, and `LeaseRenewer` sharing per user.

## APIs and Control Flow
`hasLease` and `leaseCount` inspect Namenode lease state through `NameNodeAdapter`. `testLeaseAbort` uses a spied `NamenodeProtocols` to make `renewLease` throw `InvalidToken`, simulates soft and hard renewal expiry, verifies writes continue past soft failure but fail after hard failure, confirms the renewer empties, then verifies reads and new writes still work. `testLeaseAfterRename` opens a file, renames it through several directory cases, and checks the lease follows the destination. `testLeaseAfterRenameAndRecreate` verifies inode IDs allow a renamed open file and a newly created file at the old path to coexist. `testLease` checks leases for open files and that flushing after deleting the parent fails. `testFactory` uses a mocked `ClientProtocol` to verify `DFSClient` instances for the same UGI share a renewer while different UGIs do not.

## State, Dependencies, Integration
State includes Namenode lease tables, client renewer timestamps, open streams, rename metadata, and mocked protocol responses. Dependencies include `LeaseRenewer`, `NameNodeAdapter`, `Mockito`, `UserGroupInformation`, `DFSClient`, and `NamenodeProtocols`. It integrates client lease management with namespace mutations and user identity.

## Risks and Test Signals
Signals are lease counts, path-specific lease existence, expected IO failures, renewer identity, and content checks. Risks include internal timestamp mutation (`dfs.lastLeaseRenewal`), sleep-based renewer cleanup, mocked protocol drift, and brittle exception behavior after deleted parent paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLease.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery.java

## Purpose
Tests block synchronization and lease recovery for contiguous HDFS files, including truncated metadata, failed recovery retry, append after recovery, ViewDFS integration, empty committed last blocks, aborted recovery, and committed blocks with content.

## APIs and Control Flow
`testBlockSynchronization` creates a replicated file, appends to hold a lease, expires the lease, checks generation stamps and sizes across replicas, and verifies safe mode blocks recovery. `testBlockRecoveryWithLessMetafile` truncates a block meta file, restarts a DN into recovery state, recovers the lease, and checks file length drops by one checksum chunk. `testBlockRecoveryRetryAfterFailedRecovery` finalizes one replica and deletes metadata to force retry. `testLeaseRecoveryAndAppend` and ViewDFS variant confirm another client cannot append until recovery succeeds, then can append. HDFS-14498 tests create committed-not-complete files with zero or one byte and verify manual and lease-manager recovery. `testAbortedRecovery` fakes an RBW report and completes without pipeline update, then expects the block to be dropped. `createCommittedNotCompleteFile` drives low-level Namenode create/addBlock/complete and optional aborted `DFSOutputStream` writes.

## State, Dependencies, Integration
State spans block generation stamps, metadata files, under-construction inode state, lease manager timers, safe mode, block manager internals, and client stream aborts. Dependencies include `NameNodeAdapter`, `LeaseManager`, `BlockManager`, `DataNodeTestUtils`, `TestInterDatanodeProtocol`, `DFSOutputStream`, `CryptoProtocolVersion`, and `ViewDistributedFileSystem`. It integrates low-level Namenode RPCs, DN dataset state, and public recover/append APIs.

## Risks and Test Signals
Signals include recovered file length, lease-holder disappearance, deleted block state, append/readback content, replica generation stamp equality, and safe-mode lease count. Risks are timing around lease expiry, direct block metadata corruption, low-level internal RPC usage, and environment-sensitive DN restart/recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery2.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery2.java

## Purpose
Additional slow lease-recovery tests focused on immediate recovery, close during recovery, recovery by another user, hard and soft lease expiration, and NameNode restart while recovery is in progress.

## APIs and Control Flow
`startUp` creates a five-DN cluster with small blocks and fast heartbeats. `testImmediateRecoveryOfLease` creates files with interrupted renewers and long/short lease periods, recovers via create attempts, another client, and the same client while another file remains writable. `testCloseWhileRecoverLease` pauses incremental block reports, triggers recovery, asserts close fails while under recovery, resumes heartbeats, then closes. `testLeaseRecoverByAnotherUser` verifies recovery through another user's append/create path. `testHardLeaseRecovery` kills lease renewal, shortens the hard limit, waits until located blocks are no longer under construction, and verifies the writer can no longer write. `testSoftLeaseRecovery` uses fake group mapping and another client create attempts to trigger soft recovery. Restart tests disable DN heartbeats, spy the edit log to avoid segment finalization, wait for Namenode lease-holder takeover, restart the NN, validate lease state, resume DNs, and verify data plus writer failure.

## State, Dependencies, Integration
State includes static cluster/DFS references, lease periods, DN heartbeats/IBRs, edit log behavior, under-construction blocks, and user/group mappings. Dependencies include `AppendTestUtil`, `DataNodeTestUtils`, `NameNodeAdapter`, `FSEditLog`, `LeaseManager`, `GenericTestUtils`, and Mockito spies. It integrates client lease recovery with DN reports and edit-log restart recovery.

## Risks and Test Signals
Signals are file-length/content checks, expected exceptions, missing-block count, lease-holder transitions, and writer failure after lease loss. Risks are sleep-heavy timing, static mutable configuration across tests, paused IBR/heartbeat cleanup, and restart path sensitivity to edit-log internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecoveryStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecoveryStriped.java

## Purpose
Tests lease recovery for erasure-coded striped files, safe-length calculation, stale datanode handling, and zero-length internal replica cases.

## APIs and Control Flow
`setup` configures block/cell sizes for the default EC policy, starts data+parity DNs, enables the policy, and applies it to the test directory. `BlockLengths` wraps internal block lengths and computes `StripedBlockUtil.getSafeLength`. `testLeaseRecovery` runs generated block-length suites through `runTest`; `runTest` writes partial internal blocks, recovers the lease as another user, validates data to safe length, restarts the NameNode, waits for first block report, and validates again. `testLeaseRecoveryWithStaleDataNode` marks a DN stale, recomputes safe length without that block, recovers, and checks data. `testSafeLength` checks known safe-length values. `testLeaseRecoveryWithManyZeroLengthReplica` writes one cell, waits for all streamers to ack, replaces their block streams with null outputs, and recovers. Helpers compute stop positions, wait for streamer acks/bytes sent, abort streams, and call `DistributedFileSystem.recoverLease`.

## State, Dependencies, Integration
State spans EC policy metadata, striped data streamers, internal block lengths, block streams, stale DN timestamps, old generation stamps, and block reports after NN restart. Dependencies include `DFSStripedOutputStream`, `StripedDataStreamer`, `StripedBlockUtil`, `Whitebox`, `BlockRecoveryWorker`, `StripedFileTestUtil`, and `DataNodeTestUtils`. It integrates striped client writing, DN recovery, and safe-length math.

## Risks and Test Signals
Signals are safe-length equality, successful data validation before and after restart, and recoverLease completion. Risks include randomized block-length suites, heavy internal reflection through `Whitebox`, timing on streamer ack waits, and a duplicated `StripedFileTestUtil.checkData` argument line in the displayed source would be a compile risk if present; the actual checked file should be verified before relying on this test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecoveryStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInDFS.java

## Purpose
Runs the generic `TestListFiles` suite against HDFS through `DistributedFileSystem`.

## APIs and Control Flow
`testSetUp` sets the inherited test paths to `/tmp/TestListFilesInDFS`, creates a `MiniDFSCluster`, initializes inherited `fs`, and deletes any old test directory. `testShutdown` closes `fs` and shuts down the cluster. `getTestDir` returns `/main_` for inherited tests.

## State, Dependencies, Integration
State is inherited from `TestListFiles` fixtures and HDFS namespace entries created by that suite. Dependencies are `MiniDFSCluster`, `Path`, and the superclass test contract. It integrates the common file-listing contract with HDFS.

## Risks and Test Signals
Signals are inherited tests from `TestListFiles`, not explicit methods in this file. Risks are limited local visibility into exact assertions, and static inherited fields requiring proper cleanup between suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInFileContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInFileContext.java

## Purpose
Tests `FileContext.util().listFiles` behavior on HDFS for files, directories, recursion, non-recursion, block-location metadata, and symbolic links.

## APIs and Control Flow
`testSetUp` starts a cluster and obtains `FileContext`. `writeFile` creates parent paths and writes deterministic random bytes. `testFile` lists a file with recursive true and false and checks one `LocatedFileStatus`. `testDirectory` verifies empty directory listing, one-file listing, then recursive and non-recursive ordering for nested files. `testSymbolicLinks` creates symlinks to a directory and file and checks recursive listing follows the directory symlink and non-recursive listing returns the file target. `cleanDir` deletes the test root after each test.

## State, Dependencies, Integration
State is HDFS namespace, file contents, symlink metadata, and block locations. Dependencies include `FileContext`, `Options.CreateOpts`, `CreateFlag`, `RemoteIterator`, `LocatedFileStatus`, and `FsPermission`. It integrates FileContext utility listing with HDFS block-location reporting and symlink resolution.

## Risks and Test Signals
Signals are lengths, qualified paths, block-location counts, iterator exhaustion, and ordering. Risks are ordering assumptions and HDFS symlink behavior needing symlink support enabled in the environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocalDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocalDFS.java

## Purpose
Tests basic `FileSystem` working directory and home directory behavior against a local `MiniDFSCluster`.

## APIs and Control Flow
`writeFile`, `readFile`, and `cleanupFile` create, verify, and delete simple files. `getUserName` extracts the DFS client's short username for `DistributedFileSystem`. `testWorkingDirectory` verifies the original working directory is absolute, writes relative paths, changes working directory with absolute and relative paths, reads content, cleans up, and checks home directory uses the default `/user/<user>` prefix. `testHomeDirectory` loops over custom home prefixes `/home` and `/home/user` and checks `getHomeDirectory`.

## State, Dependencies, Integration
State is per-client working directory, namespace paths, and home-prefix configuration. Dependencies include `MiniDFSCluster`, `FileSystem`, `HdfsClientConfigKeys`, and simple data streams. It integrates HDFS `FileSystem` path resolution with user identity and configuration.

## Risks and Test Signals
Signals are content equality, existence/deletion checks, and exact home path equality. Risks are user-name derivation differences for non-DFS wrappers and repeated cluster creation inside a loop with shared `Configuration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocalDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocatedBlocksRefresher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocatedBlocksRefresher.java

## Purpose
Tests `LocatedBlocksRefresher`, the DFS client background mechanism that refreshes cached block locations for tracked input streams when local dead nodes appear.

## APIs and Control Flow
`setUp` configures replication, block size, prefetch size, disables short-circuit reads, and leaves cluster creation to `setupTest`, which sets the refresh interval and unique client context. `testDisabledOnZeroInterval` expects no refresher. `testEnabledOnNonZeroInterval` expects a refresher and no refreshes without tracked streams. `testRefreshOnDeadNodes` creates a multi-block file, opens a `DFSInputStream`, checks prefetch count, registers it with the refresher, stops a DN hosting the first block, reads to mark a local dead node, waits for one refresh, verifies `locatedBlocks` object changed and dead nodes cleared, repeats with another stopped DN, then deregisters. Helpers stop hosting DNs, wait for run/refresh counters, and create a test file.

## State, Dependencies, Integration
State includes DFS client cached `LocatedBlocks`, local dead-node maps, refresher run/refresh counters, stopped DNs, and client context identity. Dependencies include `LocatedBlocksRefresher`, `DFSInputStream`, `MiniDFSCluster`, `DataNodeProperties`, `HdfsClientConfigKeys`, and `Time`. It integrates background client refresh with read failure handling.

## Risks and Test Signals
Signals are refresher nullability, tracked-stream state, run/refresh count deltas, changed block-location object identity, and cleared dead nodes. Risks are timing-based waits, stopping DNs by transfer address, prefetch count assumptions, and possible extra refreshes if dead locations remain in replicas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocatedBlocksRefresher.java -->
