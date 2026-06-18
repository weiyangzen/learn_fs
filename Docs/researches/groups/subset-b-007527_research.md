# Research: subset-b-007527

Grouped research for Hadoop HDFS tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFile.java

## Purpose
Tests `DistributedFileSystem` and `FileContext` behavior for erasure-coded files, especially block-location reporting, edit-log replay of file-level EC policy choices, and filesystem read statistics. The suite starts a `MiniDFSCluster` sized to the active EC policy's data plus parity units, enables the policy, and marks `/ec` as an EC directory.

## Important APIs and Types
Key APIs include `DistributedFileSystem.enableErasureCodingPolicy`, `DFSClient.setErasureCodingPolicy`, `FileSystem.listFiles`, `FileSystem.getFileBlockLocations`, `FileContext.listLocatedStatus`, `FileContext.getFileBlockLocations`, and `FileSystem.Statistics`. It uses `ErasureCodingPolicy`, `SystemErasureCodingPolicies`, `BlockLocation`, `LocatedFileStatus`, `MiniDFSCluster`, `MiniDFSNNTopology`, and the builder-style `createFile(...).replicate()` / `.ecPolicyName(...)` APIs.

## Control Flow
`setup()` derives cell, stripe, block, and block-group sizes from `getEcPolicy()`, configures HDFS block size and load-insensitive placement, then creates an EC-enabled `/ec` tree. `createFile` writes deterministic bytes and waits for block groups. The three block-location tests cover files smaller than one cell, exactly one stripe, and larger than one block group; each validates both `DistributedFileSystem` and `FileContext` views. `testReplayEditLogsForReplicatedFile` rebuilds the cluster with HA, writes one inherited EC file, one forced replicated file, and one explicit alternate EC-policy file, then fails over to the second NameNode and verifies policy metadata. `testStatistics` reads an EC file and checks aggregate and thread-local EC byte counters.

## State, Persistence, Dependencies, Integration
Persistent state is NameNode namespace/edit-log metadata for EC policy inheritance and per-file policy overrides. The tests depend on EC policy definitions, striped block reporting, HA edit replay, and filesystem statistics accounting. Integration points include HDFS client file creation options, NameNode policy lookup, block manager reports, and `FileContext` compatibility.

## Risks and Test Signals
High-value signals are host-count and length calculations for partial EC groups, survival of replicated and alternate-policy files through HA edit replay, and EC byte-read counter correctness. Risks are timing sensitivity around block group reports and accidental coupling to default policy geometry; the random-policy subclass broadens that coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFileWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFileWithRandomECPolicy.java

## Purpose
Runs the full `TestDistributedFileSystemWithECFile` suite with a random non-default EC policy. This validates that block-location, HA replay, explicit EC policy, replicated-file override, and statistics assumptions are not hardcoded to the default striped policy.

## Important APIs and Types
The class extends `TestDistributedFileSystemWithECFile` and overrides `getEcPolicy()`. It uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and SLF4J logging.

## Control Flow
The constructor chooses a random non-default system EC policy once per test instance and logs the inherited test class plus policy name. All setup, assertions, and cluster lifecycle remain in the superclass; this subclass only changes the policy geometry used by those inherited tests.

## State, Persistence, Dependencies, Integration
State is the selected `ErasureCodingPolicy` field. Its integration point is the superclass setup path, which computes cell size, block-group size, DataNode count, and assertions from `getEcPolicy()`. Persistence behavior is therefore inherited and retested under a different policy ID and schema.

## Risks and Test Signals
The signal is polymorphic coverage of the same DFS APIs under non-default EC geometry. The primary risk is random selection causing intermittent exposure to policy-specific timing or layout behavior; failures are useful because they show hidden default-policy assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFileWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEnclosingRoot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEnclosingRoot.java

## Purpose
Verifies `DistributedFileSystem.getEnclosingRoot` for ordinary paths and paths inside an encryption zone. The core contract is that `/` remains the enclosing root outside special roots, while an encryption zone root becomes the enclosing root for the zone and for non-existent descendants beneath it.

## Important APIs and Types
Uses `MiniDFSCluster`, `DistributedFileSystem`, `HdfsAdmin.createEncryptionZone`, `CreateEncryptionZoneFlag.NO_TRASH`, `JavaKeyStoreProvider`, `FileSystemTestHelper`, `DFSTestUtil.createKey`, and `EncryptionZoneManager` logging.

## Control Flow
`setup()` creates a JKS-backed key provider under the test root, enables delegation-token key usage, starts a one-DataNode cluster, installs the NameNode key provider into the DFS client, and creates `test_key`. The single test checks `/` and `/zone1` before zone creation, creates `/zone1` as an encryption zone, then checks the root path, the zone root, a non-existent file under the zone, and a non-existent nested directory/file under the zone.

## State, Persistence, Dependencies, Integration
State lives in the NameNode encryption-zone map and the JKS key provider. The test does not restart the cluster, so it focuses on live namespace resolution rather than fsimage/edit-log durability. It integrates the public DFS API with `HdfsAdmin` zone creation and the client-side key provider hook needed for JKS tests.

## Risks and Test Signals
The strongest signal is non-existent descendant handling, because callers can ask for enclosing roots before creating files. Risks include provider setup mistakes masking namespace behavior; teardown resets `EncryptionFaultInjector` to prevent leakage into other encryption tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEnclosingRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptedTransfer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptedTransfer.java

## Purpose
Tests encrypted DataTransferProtocol behavior for reads, writes, appends, checksum operations, key expiry, DataNode pipeline recovery, cipher negotiation, and trusted-channel bypass. It is parameterized to run with normal encrypted transfer and with `TestTrustedChannelResolver`, where trusted peers skip normal encryption-key use.

## Important APIs and Types
Important APIs include `DFS_ENCRYPT_DATA_TRANSFER_KEY`, block access tokens, `DFS_DATA_ENCRYPTION_ALGORITHM_KEY`, cipher-suite configuration, `FileSystem.getFileChecksum`, `DFSClient.shouldEncryptData`, `DFSClient.clearDataEncryptionKey`, `DFSClient.connectToDN`, and `DFSOutputStream.getPipeline`. It uses `SaslDataTransferServer`, `DataTransferSaslUtil`, `BlockTokenSecretManager`, `DataEncryptionKey`, `InvalidEncryptionKeyException`, `LocatedBlock`, and `SystemErasureCodingPolicies`.

## Control Flow
`writeUnencryptedAndThenRestartEncryptedCluster` first writes plaintext data to an unencrypted cluster, records its checksum, restarts the same storage with encrypted transfer enabled, and returns a client whose config must discover encryption from the NameNode. Read tests validate checksum preservation and log evidence for RC4/AES/default negotiation. Long-lived-client tests restart NameNode/DataNode or let block-token keys expire, then confirm transparent key refresh. Invalid-key tests spy on `DFSClient` to verify stale keys are cleared and retried for both replicated and striped checksum paths. Write tests vary DataNode counts, test append, trigger block transfer during append, and force pipeline recovery after stopping a pipeline DataNode.

## State, Persistence, Dependencies, Integration
State includes block tokens, data encryption keys, transfer cipher config, DataNode token-secret managers, and stored HDFS blocks reused across cluster restarts. Dependencies are MiniDFSCluster, Mockito, log capture, EC policy setup for striped checksum coverage, and low retry/key lifetimes for expiry tests. Integration points span DFSClient, DataNode SASL negotiation, checksum retrieval, append pipeline recovery, and trusted-channel resolver configuration.

## Risks and Test Signals
Signals include preserved file contents/checksums after enabling transfer encryption, expected SASL/cipher log lines, explicit verification that invalid keys clear the cached encryption key, and pipeline replacement after a stopped DataNode. Risks are timing sensitivity around key expiry and log-string assertions; the trusted-channel parameter prevents false assumptions that every successful transfer used encryption keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptedTransfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZones.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZones.java

## Purpose
Provides broad integration coverage for HDFS transparent encryption zones. It covers zone creation/listing/querying, permissions, key-provider discovery, file encryption info, read/write correctness, snapshots, trash, raw paths, WebHDFS behavior, fsck/OIV compatibility, delegation tokens, and race handling during encrypted file creation.

## Important APIs and Types
Primary APIs include `HdfsAdmin.createEncryptionZone`, `listEncryptionZones`, `getEncryptionZoneForPath`, `provisionEncryptionZoneTrash`, `DistributedFileSystem.getEZForPath`, `CryptoAdmin`, `FsShell`, `WebHdfsFileSystem`, `DFSClient.getKeyProviderUri`, `addDelegationTokens`, `getLocatedBlocks`, snapshot APIs, and `DFSOutputStream.SUPPORTED_CRYPTO_VERSIONS`. Important types include `EncryptionZone`, `FileEncryptionInfo`, `KeyProvider`, `Credentials`, `Token`, `EncryptionFaultInjector`, `FsServerDefaults`, `CryptoInputStream`, `PBImageXmlWriter`, `DFSck`, and `SnapshotDiffReport`.

## Control Flow
`setup()` creates a JKS key provider, starts a one-DataNode cluster, installs the provider into the client, enables a small listing batch size, and creates `test_key`. Tests then exercise feature clusters: basic create/list validation and namespace persistence; root and fully qualified paths; non-superuser list/get access; rename constraints across or within zones; encrypted reads/writes before and after key roll; WebHDFS reads/appends and redirect behavior; cipher/protocol negotiation failure and success; missing provider errors; `FileStatus.isEncrypted`; snapshots and snapshot diffs; symlink and concat restrictions; fsck/OIV XML parsing; root/relative/non-existent path handling; trash roots for nested/root zones; provider URI lookup from credentials, server defaults, and ignore flags; and raw reserved path writes. `testStartFileRetry` uses `EncryptionFaultInjector` and latches to simulate races while generating EDEKs.

## State, Persistence, Dependencies, Integration
Persistent state includes encryption-zone xattrs/metadata, fsimage/edit-log records, key versions, encrypted data encryption keys, snapshots, trash directories, and delegation-token credentials. Dependencies include JKS key provider plumbing, NameNode encryption-zone manager, client/server defaults, WebHDFS HTTP redirects, snapshot manager, FsShell, and offline image viewer. The test integrates public admin APIs with raw DFS client metadata and shell/tool behavior.

## Risks and Test Signals
Signals are numerous: zone counts and metrics, expected authorization failures, file byte equality despite encrypted storage, different EDEKs after key roll, snapshot-specific zone metadata, healthy fsck output, parseable OIV XML, correct trash-root placement, KMS URI fallback behavior, WebHDFS raw-vs-decrypted stream checks, and retry count behavior during zone races. Risks are broad setup complexity, mutable static crypto-version fields, timing in concurrency tests, and reliance on exact exception/log messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZones.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithHA.java

## Purpose
Tests encryption-zone metadata replication across HDFS HA failover. The intended guarantee is that a standby NameNode catches up on encryption-zone edits and can serve correct zone metadata and decrypted file reads after becoming active.

## Important APIs and Types
Uses `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `HAUtil.setAllowStandbyReads`, `HdfsAdmin`, `JavaKeyStoreProvider`, `KeyProviderCryptoExtension`, and `DFSTestUtil.createKey`.

## Control Flow
`setupCluster()` enables fast edit tailing, creates a two-NameNode HA cluster, transitions NameNode 0 active, configures a failover filesystem, creates the same test key on both NameNodes, and points the DFS client at NameNode 0's provider. The test creates `/enc` as an encryption zone, adds a child directory and file, records file contents, waits for standby catch-up, shuts down NameNode 0, transitions NameNode 1 active, then verifies zone lookup for the root and child plus file content preservation.

## State, Persistence, Dependencies, Integration
State is HA-shared namespace edits for encryption-zone creation and encrypted-file metadata, plus both NameNodes' key providers. The test integrates failover client configuration, standby edit tailing, `HdfsAdmin` against each NameNode URI, and encrypted read paths after failover.

## Risks and Test Signals
The main signal is successful lookup and read on the new active after the original active is shut down. Risks include false failures if standby edit tailing lags; the explicit catch-up wait reduces this.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithKMS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithKMS.java

## Purpose
Runs the base encryption-zone suite with a MiniKMS-backed provider and adds KMS-specific tests for EDEK cache population, cache warmup after NameNode restart, and KMS delegation-token retrieval through DFS and WebHDFS.

## Important APIs and Types
Extends `TestEncryptionZones`. Uses `MiniKMS`, `KMSClientProvider`, `LoadBalancingKMSClientProvider`, `KMSDelegationToken`, `Whitebox.getInternalState`, `WebHdfsFileSystem.addDelegationTokens`, and NameNode EDEK cache loader configuration.

## Control Flow
`setup()` creates a unique MiniKMS config directory, starts MiniKMS, then invokes the inherited JKS-oriented setup with `getKeyProviderURI()` overridden to a `kms://` URI. `setProvider()` is intentionally empty because the KMS provider is resolved through configuration rather than manually installed into the DFS client. Extra tests create zones and inspect the underlying KMS client queue, call `fs.addDelegationTokens` twice to verify token reuse, restart the NameNode with zero EDEK cache-loader delay and wait for cache refill, and validate that WebHDFS returns a KMS delegation token.

## State, Persistence, Dependencies, Integration
State includes MiniKMS process/configuration, KMS client provider queues, NameNode EDEK cache state, and user credentials. Integration points are the inherited encryption-zone tests plus real KMS protocol wiring, delegation-token extension support, and cache-loader startup behavior.

## Risks and Test Signals
Signals are positive queue sizes for zone keys, stable token counts, KMS token kind from WebHDFS, and cache refill after restart. Risks include MiniKMS lifecycle failures and reflective access to provider internals, but the subclass gives stronger coverage than mocked providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithKMS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodeBenchmarkThroughput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodeBenchmarkThroughput.java

## Purpose
Tests the `ErasureCodeBenchmarkThroughput` tool against a live MiniDFSCluster for replicated and EC data paths. It validates that benchmark subcommands run successfully and that cleanup removes generated EC files.

## Important APIs and Types
Uses `ToolRunner.run`, `ErasureCodeBenchmarkThroughput`, `MiniDFSCluster`, `DistributedFileSystem.enableErasureCodingPolicy`, `FileSystem.listStatus`, `PathFilter`, and tool constants such as `EC_DIR`, `REP_DIR`, and `getFilePath`.

## Control Flow
`setup()` starts a cluster with enough DataNodes for the benchmark EC policy and enables that policy. `runBenchmark` asserts that each tool invocation returns `0`. `testReplicaReadWrite` runs `write`, `gen`, and `read` for replicated mode. `testECReadWrite` does the same for EC mode. `testCleanUp` generates EC files, runs `clean`, then filters the EC directory for the expected benchmark filename prefix and asserts zero matches.

## State, Persistence, Dependencies, Integration
State is test data written under the benchmark's replicated and EC directories. The tests depend on the benchmark tool's command parser, worker behavior, and path naming scheme. Integration is intentionally tool-level rather than direct DFS API calls.

## Risks and Test Signals
The key signal is command success across write/generate/read/clean flows. The cleanup assertion is the only content-level verification; throughput values are not validated, so regressions in performance reporting could pass if command exits remain successful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodeBenchmarkThroughput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingAddConfig.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingAddConfig.java

## Purpose
Verifies the configuration gate controlling addition of user-defined erasure coding policies. It ensures `dfs.namenode.ec.userdefined.policy.allowed` blocks additions when false and permits them when true.

## Important APIs and Types
Uses `DFS_NAMENODE_EC_POLICIES_USERPOLICIES_ALLOWED_KEY`, `DistributedFileSystem.addErasureCodingPolicies`, `AddErasureCodingPolicyResponse`, `ErasureCodingPolicy`, and `ECSchema`.

## Control Flow
Each test creates a fresh `HdfsConfiguration`, sets the policy-allowance flag, starts a zero-DataNode MiniDFSCluster, constructs an RS(5,3) policy with a 1 MiB cell size, and calls `addErasureCodingPolicies`. The disabled case asserts `isSucceed() == false` and the precise error message. The enabled case asserts success and a null error.

## State, Persistence, Dependencies, Integration
No file data is written. The relevant state is NameNode EC policy manager configuration and in-memory policy addition response. The zero-DataNode cluster emphasizes that policy validation is a NameNode/admin-plane operation independent of block placement.

## Risks and Test Signals
Signals are exact response success/error fields. The disabled test is sensitive to error-message wording, but this is useful for client-visible contract stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingAddConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingExerciseAPIs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingExerciseAPIs.java

## Purpose
Exercises broad `FileSystem` and `HdfsAdmin` APIs with erasure coding enabled at the root. The test asserts that ordinary namespace, security, metadata, cache, snapshot, storage-policy, encryption-zone, and file APIs still work for EC directories/files, while EC-unsupported append and truncate fail.

## Important APIs and Types
APIs include ACL methods, xattrs, quotas, cache pools/directives, snapshots, symlinks, file create/open/concat/checksum/rename/delete, storage policies, EC policy add/disable/remove/set/unset, encryption-zone creation/reencryption, and delegation tokens. Important types include `AclEntry`, `AclStatus`, `CachePoolInfo`, `CacheDirectiveInfo`, `SnapshotDiffReport`, `FileEncryptionInfo`, `LocatedBlocks`, `BlockStoragePolicySuite`, `ECSchema`, and `Credentials`.

## Control Flow
`setupCluster()` enables ACLs, configures a JKS key provider, starts enough DataNodes for the default EC policy, enables all EC policies, and sets the root EC policy. Tests then independently validate access/owner/time metadata, quota summaries, cache operations, EC policy lifecycle, ACL mutation, xattr CRUD, snapshot lifecycle and diff report, symlink status, file operations including concat and checksum stability across rename, encryption-zone file metadata and reencrypt start, storage-policy set/unset, and expected failures for append/truncate.

## State, Persistence, Dependencies, Integration
State spans root-inherited EC policy, per-file EC layout, ACL and xattr metadata, snapshots, cache manager state, key-provider state, encryption-zone EDEKs, delegation credentials, and storage policy metadata. Dependencies include MiniDFSCluster, JKS provider setup, ACL enablement, all system EC policies, and helper wrappers.

## Risks and Test Signals
Signals are successful completion of many public APIs under EC plus explicit append/truncate exceptions. Risks include broad tests masking exact failure sources and some assertions checking no-op semantics, but the suite is valuable as a regression net for cross-feature EC compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingExerciseAPIs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingMultipleRacks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingMultipleRacks.java

## Purpose
Tests rack-aware placement for erasure-coded block groups when racks have skewed DataNode counts. The goal is to ensure placement succeeds and, where possible, remains rack-failure tolerant even in unbalanced topologies.

## Important APIs and Types
Uses `DFSTestUtil.setupCluster`, `DistributedFileSystem.setErasureCodingPolicy`, `DFSTestUtil.writeFile`, `getFileBlockLocations`, `DFSTestUtil.waitForReplication`, `ExtendedBlock`, and topology path parsing. It enables trace/debug logging for `BlockPlacementPolicy`, `BlockPlacementPolicyDefault`, `BlockPlacementPolicyRackFaultTolerant`, and `NetworkTopology`.

## Control Flow
`setup()` selects the EC policy and disables load consideration so placement behavior dominates. `setupCluster` creates a cluster with requested DataNode/rack skew and applies the EC policy to `/`. `testSkewedRack1` covers a two-rack extreme with one single-DN rack. `testSkewedRack2` covers many single-DN racks plus one larger rack. `testSkewedRack3` writes several files in a topology where two racks have enough nodes and asserts no rack receives more blocks than the parity-unit count.

## State, Persistence, Dependencies, Integration
State is block-placement metadata and rack topology strings. The tests depend on MiniDFSCluster topology construction and the rack-fault-tolerant placement policy. There is no restart persistence coverage.

## Risks and Test Signals
Signals are full block-group host counts and rack-count bounds. Risks are topology parsing assumptions and possible flakiness if placement behavior changes with load consideration, which the test disables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingMultipleRacks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicies.java

## Purpose
Tests the main HDFS erasure-coding policy contract: inheritance, file-level override, replicated override, listing/status reporting, permission checks, user-defined policy validation, policy-manager limits, reserved raw paths, persistence through restarts, and coexistence of multiple system policies.

## Important APIs and Types
Important APIs include `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `getErasureCodingPolicy`, `getAllErasureCodingPolicies`, `addErasureCodingPolicies`, `getAllErasureCodingCodecs`, `createFile().ecPolicyName(...)`, `createFile().replicate()`, `DFSClient.create`, `setReplication`, and `listPaths`. Types include `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, `SystemErasureCodingPolicies`, `ErasureCodingPolicyManager`, `ECSchema`, `HdfsFileStatus`, `INodeFile`, `ContentSummary`, and `AccessControlException`.

## Control Flow
The setup starts enough DataNodes for the selected policy and enables all EC policies. Tests then cover replicated files already under a directory later marked EC, content summary inheritance, basic set-policy behavior and restart/fsimage loading, legal moves between EC and non-EC directories, setReplication no-op behavior on EC files, reserved `/.reserved/raw` policy mapping, invalid/default policy setting, listing all policies/codecs, missing-path failures, multiple policy coexistence, permission enforcement for normal users versus superuser, file-level EC policy override, explicit replicated file creation under EC parents, invalid user-defined policies, maximum user-defined policy IDs, replication policy hiding, and different cell-size policies.

## State, Persistence, Dependencies, Integration
State includes EC policy xattrs/IDs on directories and files, INode striped flags, policy-manager registry entries, user-defined policy IDs, permissions, fsimage/edit-log records, and content summary metadata. Integration spans public `DistributedFileSystem`, lower-level `DFSClient`, `HdfsAdmin`, NameNode `FSNamesystem`/INode inspection, and user impersonation.

## Risks and Test Signals
Signals include exact policy equality on files/directories/listings, null policy for replicated overrides, exceptions for invalid policies and missing paths, access-denied behavior, ID exhaustion failure, and policy retention after NameNode restart. Risks include broad stateful coverage and some swallowed exception patterns, but it is the central regression suite for EC policy semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPoliciesWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPoliciesWithRandomECPolicy.java

## Purpose
Runs the `TestErasureCodingPolicies` suite using a random non-default EC policy. This expands the policy semantics tests beyond the default policy and catches hidden assumptions about data/parity unit counts, cell sizes, and policy IDs.

## Important APIs and Types
Extends `TestErasureCodingPolicies` and overrides `getEcPolicy()`. Uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and logging.

## Control Flow
The constructor selects a random non-default policy and logs the superclass and policy name. All tests are inherited; the superclass setup consumes this policy to size the MiniDFSCluster and to drive policy assertions.

## State, Persistence, Dependencies, Integration
The only local state is the selected policy field. Persistence, permission, listing, file-level override, replicated override, and policy-manager behavior are inherited from the superclass but executed with alternate policy geometry.

## Risks and Test Signals
The signal is repeated central policy coverage under varied system policy selection. The risk is nondeterministic policy choice, which can make failures policy-dependent; logs include the selected policy for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPoliciesWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshot.java

## Purpose
Tests interactions between erasure-coding policy metadata and HDFS snapshots. It verifies snapshots preserve the policy state visible at snapshot time, copied snapshots do not preserve EC policy metadata, and EC `FileStatus` flags survive NameNode restart.

## Important APIs and Types
Uses `allowSnapshot`, `createSnapshot`, `deleteSnapshot`, `getErasureCodingPolicy`, `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, safe mode/saveNamespace/restart, `FsShell -cp -px`, `ContractTestUtils.assertErasureCoded`, and `SystemErasureCodingPolicies`.

## Control Flow
Setup starts a cluster with `data + parity` DataNodes and enables the selected EC policy. Tests snapshot a parent directory containing an EC directory, delete/recreate the directory, take additional snapshots, and verify each snapshot path reports the historical policy or null. Other tests snapshot the EC directory itself, restart the NameNode after saving namespace, copy a snapshot and assert the copy lacks EC policy, compare normal and EC `FileStatus` before/after restart, verify `.snapshot` itself returns null rather than throwing, and create snapshots across policy changes from null to RS-6-3 to unset to RS-3-2.

## State, Persistence, Dependencies, Integration
State includes snapshot inode references, EC policy xattrs/IDs, file contents, fsimage persistence, and file status flags. Integration points are snapshot manager, EC policy manager, FsShell copy semantics, NameNode restart, and contract-test utilities.

## Risks and Test Signals
Signals are precise policy equality/nullness on snapshot paths, content preservation, copied snapshot policy absence, and restart-stable `isErasureCoded` status. Risks are path construction around snapshot names and assumptions about copy behavior, but these are exactly the client-visible contracts under test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshotWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshotWithRandomECPolicy.java

## Purpose
Runs `TestErasureCodingPolicyWithSnapshot` with a random non-default EC policy. It ensures snapshot metadata preservation and restart behavior are not tied to the default EC policy.

## Important APIs and Types
Extends `TestErasureCodingPolicyWithSnapshot`, overrides `getEcPolicy()`, and uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and logging.

## Control Flow
The constructor selects and logs a random non-default policy. The inherited setup uses that policy to choose DataNode count and enable the policy; all inherited snapshot, copy, and restart tests then run with the alternate policy.

## State, Persistence, Dependencies, Integration
Local state is the selected policy. Snapshot metadata, fsimage persistence, and file-status behavior are inherited from the superclass and exercised under a different policy ID/schema.

## Risks and Test Signals
The main signal is policy-agnostic snapshot behavior. Randomness can make results policy-specific, but the log records the policy name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshotWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExtendedAcls.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExtendedAcls.java

## Purpose
Tests HDFS extended ACL inheritance and access enforcement for directories and files. The suite focuses on default ACL propagation, immutability of already-created children when parent defaults change, non-inheritance of access ACLs, granting extra access in subdirectories, and restricting inherited access in subdirectories.

## Important APIs and Types
Uses `setAcl`, `modifyAclEntries`, `removeAcl`, `getAclStatus`, `setPermission`, `access`, `UserGroupInformation.doAs`, `AclEntry`, `AclStatus`, `FsPermission`, and `FsAction`. Helpers come from `AclTestHelpers.aclEntry`.

## Control Flow
`setup()` enables NameNode ACL support and starts a three-DataNode cluster. `testDefaultAclNewChildDirFile` sets a parent default ACL and verifies new directories receive access plus default ACL entries while new files receive access entries. `testDefaultAclExistingDirFile` shows existing children retain old inherited ACLs after parent ACL changes/removal. `testAccessAclNotInherited` confirms only default ACLs propagate. `testGradSubdirMoreAccess` adds a group default ACL to a child directory and verifies group access only below that child. `testRestrictAtSubDir` changes a child default ACL to deny a group and verifies parent access remains broader than child access. `tryAccess` impersonates users and maps `AccessControlException` to boolean results.

## State, Persistence, Dependencies, Integration
State is ACL entries on inodes, permission bits and masks, generated child ACLs, and user/group identity in UGI. The tests do not restart the cluster, so persistence to fsimage/edit logs is not covered here. Integration points are NameNode ACL evaluation, filesystem metadata mutation, and access checks through impersonated clients.

## Risks and Test Signals
Signals are exact ACL entry arrays and boolean access decisions for named users/groups. Risks include brittleness to ACL entry ordering and mask-calculation changes, but exact ordering is part of the current returned `AclStatus` contract these tests protect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExtendedAcls.java -->
