# Research Report: subset-b-007556

Grouped source research for Hadoop HDFS NameNode startup, storage restore, striped inode, XAttr, fine-grained locking, HA bootstrap, observer-read, and HA upgrade test sources. Each source file has its own marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartup.java

## Purpose

`TestStartup` is a broad NameNode startup and checkpoint regression suite. It validates checkpoint import from secondary storage, fsimage compression and checksum handling, fallback between multiple name directories, EC policy persistence after image fallback, DataNode reregistration after NameNode restart, XAttr startup configuration validation, read-only storage-dir rejection, stale-storage metrics after restart, and configured name-dir permissions.

## Important APIs, Types, and Functions

The fixture builds `HdfsConfiguration` with explicit name, edits, checkpoint, DataNode, and secondary HTTP paths under `MiniDFSCluster.getBaseDirectory()`. Helpers include `createCheckPoint`, `corruptFSImageMD5`, `corruptNameNodeFiles`, `checkNameNodeFiles`, `verifyDifferentDirs`, and `checkNameSpace`. The tests exercise `MiniDFSCluster`, `SecondaryNameNode`, `NameNode`, `FSImage`, `NNStorage`, `NamenodeProtocols`, `MD5FileUtils`, `FSNamesystem.getNamespaceDirs`, `BlockManagerTestUtil.checkHeartbeat`, JMX `FSNamesystemState`, and `HostsFileWriter`.

## Control Flow

The checkpoint-import tests start a cluster and secondary, create files, checkpoint, corrupt primary NameNode directories, then restart with `StartupOption.IMPORT` and assert image/edit files were restored to the expected directory types and sizes. Compression tests repeatedly start a standalone `NameNode`, verify `/test`, enter safe mode, save namespace, and restart under different compression settings. Checksum tests corrupt MD5 sidecars and assert full corruption aborts startup while one bad directory can fall back. Later tests restart NameNodes, change storage permissions, trigger block reports, and inspect live reports or MBean counters.

## State and Persistence Behavior

The class mutates on-disk `current` directories, `fsimage_*`, `edits_*`, MD5 files, checkpoint directories, include-host files, and local file permissions. It also observes persistent namespace state such as directories, erasure coding policy enablement, XAttrs, storage stale flags, and NameNode dir permissions across shutdown and restart.

## Dependencies and Integration Points

It integrates NameNode storage, SecondaryNameNode checkpointing, DFS clients, EC policy manager, DataNode heartbeat/block-report paths, NameNode JMX, local filesystem permissions, and cluster host include files. The tests are mostly end-to-end and rely on MiniDFSCluster lifecycle cleanup.

## Risks and Edge Cases

The tests cover dangerous startup edges: corrupted checksums, missing primary storage, losing EC enabled-policy state during fallback, read-only name dirs, stale DataNode storage state after reregistration, and invalid XAttr limits. They are sensitive to local filesystem permissions, JMX availability, host resolution, and correct cleanup of cluster processes.

## Test Signals

Signals include successful checkpoints/import, expected `IOException` on fully corrupt fsimage, fallback startup with one bad MD5, EC file policy and enabled-policy preservation, live DataNode reports after restart, `IllegalArgumentException` messages for invalid XAttr limits, `InconsistentFSStateException` for read-only dirs, `NumStaleStorages == 0`, and octal permission matches for each name dir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupOptionUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupOptionUpgrade.java

## Purpose

`TestStartupOptionUpgrade` verifies how `NNStorage.processStartupOptionsForUpgrade` chooses a cluster ID during `-upgrade` and `-upgradeOnly` startup paths for pre-federation and federation layout versions.

## Important APIs, Types, and Functions

The parameterized class runs each test for `StartupOption.UPGRADE` and `StartupOption.UPGRADEONLY`. It creates empty-list `NNStorage` instances, mutates `StartupOption.setClusterId`, sets storage cluster IDs directly, and uses `LayoutVersion.Feature.RESERVED_REL20_204`, `RESERVED_REL22`, and `FEDERATION` layout versions.

## Control Flow

Each test prepares `startOpt`, `layoutVersion`, and current storage cluster ID state, calls `processStartupOptionsForUpgrade`, then asserts the resulting `storage.getClusterID()`. Pre-0.22 upgrade without a cluster ID generates a new `CID...`; 0.22 upgrade with a user ID uses the supplied ID; federation-to-federation upgrades preserve the existing cluster ID even if a user passes a different one.

## State and Persistence Behavior

Only in-memory `NNStorage` metadata is mutated. The tested behavior is persistence-critical because this cluster ID is written into NameNode storage versions during real upgrades.

## Dependencies and Integration Points

The class integrates the NameNode storage upgrade parser with `StartupOption` command-line state and layout-version feature gates. It protects federation upgrade compatibility.

## Risks and Edge Cases

Incorrect behavior can split a federated cluster by changing cluster IDs or fail older upgrades that need a generated ID. The parameterized constructor calls `setUp`, so shared mutable `StartupOption` state must be reset before each parameter run.

## Test Signals

Passing assertions show generated IDs start with `CID`, explicit IDs are honored for older non-federated upgrade, and existing federation IDs win over absent, wrong, or matching command-line IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupOptionUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupProgressServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupProgressServlet.java

## Purpose

`TestStartupProgressServlet` verifies the JSON emitted by `StartupProgressServlet` for empty, running, and complete NameNode startup progress state.

## Important APIs, Types, and Functions

The fixture uses Mockito to provide a `ServletContext` containing a `StartupProgress` under `NameNodeHttpServer.STARTUP_PROGRESS_ATTRIBUTE_KEY`, mocks request/response, and calls the real `doGet`. It uses helper state builders from `StartupProgressTestHelper`, Jetty `JSON.toString`, and `ImmutableMap` expected bodies.

## Control Flow

Each test configures a `StartupProgress` snapshot, calls `doGetAndReturnResponseBody`, removes nondeterministic `elapsedTime` fields through `filterJson`, and compares the exact JSON structure. Expected output always has top-level `percentComplete` and `phases`; phase entries include name, description, status, completion fraction, and step details.

## State and Persistence Behavior

The servlet reads in-memory startup progress only. No persistent state is changed. The test intentionally filters elapsed time because it changes at runtime.

## Dependencies and Integration Points

This is an HTTP-layer contract test between NameNode startup progress tracking and web UI/API consumers. It depends on phase and step names such as `LoadingFsImage`, `LoadingEdits`, `SavingCheckpoint`, `SafeMode`, `Inodes`, and `AwaitingReportedBlocks`.

## Risks and Edge Cases

The exact JSON comparison catches field renames, ordering changes, status regressions, and percentage calculation changes. It is brittle to intentional schema evolution and only ignores elapsed-time volatility.

## Test Signals

Signals are exact equality against pending state at `0.0`, running state at `0.375` with fsimage complete and edits half complete, and final state at `1.0` with all phases complete and populated steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupProgressServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySatisfierWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySatisfierWithHA.java

## Purpose

`TestStoragePolicySatisfierWithHA` validates that Storage Policy Satisfier mode cannot be dynamically changed on a standby NameNode in an HA cluster.

## Important APIs, Types, and Functions

The class builds a simple HA `MiniDFSCluster` with three DataNodes, two storages per DataNode, all-DISK storage types, configured capacities, and `DFS_STORAGE_POLICY_SATISFIER_MODE_KEY` set to `EXTERNAL`. It calls `NameNode.reconfigurePropertyImpl` and expects `ReconfigurationException`.

## Control Flow

`createCluster` configures block size, SPS mode, and a short SPS DataNode cache refresh interval, then starts HA topology and transitions NN0 active. The test transitions NN0 to standby, waits for cluster activity, tries to reconfigure SPS mode from `EXTERNAL` to `NONE`, and asserts the high-level and cause messages.

## State and Persistence Behavior

Cluster state includes HA NameNode role transitions and runtime reconfiguration state. No namespace data is written; the important persistent-style contract is that standby nodes must not start or stop SPS service through reconfiguration.

## Dependencies and Integration Points

It integrates HA state management, `MiniDFSNNTopology.simpleHATopology`, storage type/capacity cluster builder paths, and the NameNode reconfiguration subsystem for SPS configuration.

## Risks and Edge Cases

Allowing SPS mode changes on standby could desynchronize service lifecycle from HA role ownership. The test only covers disabling `EXTERNAL` on standby, not all possible SPS mode transitions.

## Test Signals

The expected signal is `ReconfigurationException` containing the attempted property change plus a cause mentioning that enabling or disabling SPS on standby is not allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySatisfierWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySummary.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySummary.java

## Purpose

`TestStoragePolicySummary` verifies aggregation, canonical formatting, policy matching annotations, and descending-count sorting for `StoragePolicySummary`.

## Important APIs, Types, and Functions

The test uses `BlockStoragePolicySuite.createDefaultSuite`, `BlockStoragePolicy` instances for `HOT`, `WARM`, and `COLD`, `StorageType` arrays, `StoragePolicySummary.add`, `StoragePolicySummary.sortByComparator`, and `StorageTypeAllocation.toString`.

## Control Flow

Each test adds synthetic block storage allocations under specified policies, converts the internal `storageComboCounts` map into an ordered string map, and compares exact expected strings and counts. Scenarios cover repeated HOT counts, equivalent WARM allocations in different storage-type order, mismatches between specified and actual policy, and sorting by descending count.

## State and Persistence Behavior

State is the in-memory summary map from `StorageTypeAllocation` to occurrence count. There is no persistence, but the output format is CLI/report-facing behavior.

## Dependencies and Integration Points

This tests NameNode reporting around block storage policy summaries. It depends on default policy definitions and the textual representation used to explain whether actual storage types match the requested policy.

## Risks and Edge Cases

Incorrect canonicalization can double-count equivalent allocations with different input ordering. Incorrect matching can hide policy violations. Sorting instability can change user-visible reports.

## Test Signals

Signals include exact strings such as `HOT|DISK:3(HOT)` and `COLD|DISK:1,ARCHIVE:2(WARM)`, expected map sizes, expected counts, and ordered string output for descending count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStorageRestore.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStorageRestore.java

## Purpose

`TestStorageRestore` validates NameNode failed-storage restoration for name and edits directories, including checkpoint-driven reactivation, dfsadmin toggling, multiple secondary checkpoint races, and permission-based restore failures.

## Important APIs, Types, and Functions

The fixture configures two image+edits dirs (`name1`, `name2`) and one edits-only dir (`name3`) with `DFS_NAMENODE_NAME_DIR_RESTORE_KEY=true`. Helpers include `invalidateStorage`, which reports storage errors and injects edit-log write faults by spying `EditLogOutputStream`, and `printStorages`. Tests use `FSImage`, `NNStorage`, `JournalSet.JournalAndStream`, `FileJournalManager`, `SecondaryNameNode`, `FSImageTestUtil`, `CLITestCmdDFS`, and `DFSAdmin -restoreFailedStorage`.

## Control Flow

The main restore test starts a cluster and secondary, creates a directory, invalidates selected storage dirs, creates another directory, verifies edits diverge, checkpoints to restore failed dirs, verifies fsimage and edits placement by txid, performs another edit, and confirms all active logs match through clean shutdown. Other tests toggle restore via dfsadmin, simulate an incomplete checkpoint from one secondary followed by a complete checkpoint from another, and remove permissions so restoration fails until permissions are restored.

## State and Persistence Behavior

This class directly inspects and mutates on-disk `current` storage directories, image files, finalized and in-progress edit logs, permissions, and the storage restore flag. It tests whether restored directories keep useful old images but receive fresh log segments and later finalized logs.

## Dependencies and Integration Points

It integrates storage error reporting, edit log journal streams, checkpoint upload/download, SecondaryNameNode behavior, dfsadmin CLI plumbing, and platform-specific permission handling through `Shell.WINDOWS`.

## Risks and Edge Cases

Serving an empty restored directory to a checkpoint client can lose namespace edits. Restoring only some directories can create mismatched edit logs. Permission behavior differs by OS. Fault injection through Mockito spies must target the active current stream.

## Test Signals

Signals include divergent edits before restore, matching `fsimage_4` only in image dirs, missing finalized logs in failed dirs for the old segment, matching new in-progress logs across all dirs, MD5 changes after new edits, dfsadmin output containing `restoreFailedStorage is set to true`, path survival after restart, and storage-dir counts changing from one back to three.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStorageRestore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStripedINodeFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStripedINodeFile.java

## Purpose

`TestStripedINodeFile` verifies `INodeFile` behavior for erasure-coded striped files: constructor validation, block group accounting, quota usage, under-construction size semantics, deletion marking, and storage-policy handling for striped placement.

## Important APIs, Types, and Functions

The class uses `INodeFile`, `BlockInfoStriped`, `ErasureCodingPolicyManager`, `StripedFileTestUtil.getDefaultECPolicy`, `QuotaCounts`, `BlockStoragePolicySuite`, `MiniDFSCluster`, `DistributedFileSystem`, `ClientProtocol`, `LocatedBlocks`, and `NameNodeProxies`. `createStripedINodeFile` creates a cold striped inode with default EC policy ID and preferred block size 1024.

## Control Flow

Unit-style tests create striped block groups and assert total internal block count, storage consumed formulas, file size, under-construction file size, and quota deltas. Constructor tests reject invalid combinations of replication, EC policy ID, and block type. Cluster tests create EC and contiguous files, capture their `BlockInfo` arrays, delete containing directories, and assert blocks are marked deleted. The storage-policy test creates SSD/DISK DataNodes, sets `ONE_SSD` on an EC directory, writes a striped file, and asserts located block storage types fall back to DISK.

## State and Persistence Behavior

Most tests mutate in-memory inode/block state. Cluster tests persist EC policy and files in a MiniDFS namespace and observe block deletion flags and block locations. The storage-policy test validates placement decisions visible through client block reports.

## Dependencies and Integration Points

It integrates erasure coding policy initialization, NameNode inode accounting, quota code, block deletion state, DFS client file creation, block manager placement, and supported storage-policy rules for striped files.

## Risks and Edge Cases

Striped space accounting is easy to miscalculate for partial stripes and under-construction block groups. Constructor validation prevents impossible inode states. Ignoring unsuitable storage policies for EC is important to avoid under-replicated or unavailable striped block groups.

## Test Signals

Signals include `IllegalArgumentException` for invalid EC IDs or layout arguments, total block count `9`, consumed space values `4`, `8`, `400`, and `9216`, under-construction `computeFileSize(false,false)==0`, deleted block flags after directory deletion, and all located storage types equal to `DISK` despite `ONE_SSD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStripedINodeFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTransferFsImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTransferFsImage.java

## Purpose

`TestTransferFsImage` validates client-side fsimage download error reporting, partial success across multiple local destination files, and read timeout behavior for image download and upload.

## Important APIs, Types, and Functions

The tests call `TransferFsImage.getFileClient` and `TransferFsImage.uploadImageFromStorage`, use `DFSUtil.getInfoServer`, mocked `NNStorage`, `NameNodeFile.IMAGE`, `HttpServer2`, `HttpServerFunctionalTest`, and a nested `TestImageTransferServlet` whose `doGet` and `doPut` wait for five seconds.

## Control Flow

Download error tests start a no-DataNode MiniDFSCluster and request `getimage=1&txid=0` into invalid and valid local paths. The all-invalid case expects an `IOException` and storage error reporting; the mixed case expects only the bad path to be reported and the valid file to receive data. Timeout tests start a local servlet, set `TransferFsImage.timeout=2000`, invoke download or upload, and expect `SocketTimeoutException` with `Read timed out`.

## State and Persistence Behavior

The class writes a valid local destination file and a temporary mock image file. It mutates the static `TransferFsImage.timeout`, which can affect following tests if not reset by the wider suite.

## Dependencies and Integration Points

It tests the HTTP image-transfer client path, NameNode storage error callbacks, servlet transport behavior, and storage lookup used by checkpoint/image upload flows.

## Risks and Edge Cases

If one local destination fails, successful destinations must still be usable. Download failures must mark the associated storage file bad. Static timeout mutation is a cross-test risk. The servlet delay makes timing-sensitive assertions dependent on configured timeout.

## Test Signals

Expected signals are `mockStorage.reportErrorOnFile` for invalid destinations, valid output file length greater than zero, `IOException` text containing `Unable to download to any storage`, and `SocketTimeoutException` messages equal to `Read timed out` for both GET and PUT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTransferFsImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTruncateQuotaUpdate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTruncateQuotaUpdate.java

## Purpose

`TestTruncateQuotaUpdate` verifies storage-space quota deltas computed by `INodeFile.computeQuotaDeltaForTruncate` with and without snapshots and with snapshot/current block divergence.

## Important APIs, Types, and Functions

The helper builds mock `INodeFile` instances with `BlockInfoContiguous` blocks, `PermissionStatus`, fixed `BLOCKSIZE=1024`, replication `4`, and monotonically increasing block/genstamp/inode IDs. `addSnapshotFeature` creates a mocked `FileDiff`, a `FileDiffList`, injects a `DiffListByArrayList` using `Whitebox`, and attaches `FileWithSnapshotFeature`.

## Control Flow

Tests create a 2.5-block file and compute quota delta for truncation to 1.5 blocks, one block, and zero. Without snapshots, the delta removes current replicated bytes. With snapshots and no divergence, truncating inside a snapshotted block may require allocating a new full block and boundary/zero truncates do not reclaim snapshot-retained blocks. With divergence, current blocks not present in the snapshot can be reclaimed while snapshotted blocks remain charged.

## State and Persistence Behavior

All state is in-memory inode, block, and snapshot diff state. The behavior is persistence-relevant because snapshot diffs keep old block references alive after namespace operations.

## Dependencies and Integration Points

The test targets namespace quota accounting across inode block arrays, snapshot diff lists, and truncate code. It depends on internal snapshot feature representation and uses Whitebox to construct minimal state.

## Risks and Edge Cases

Quota deltas must avoid double-counting snapshotted blocks while accounting for replacement blocks needed for copy-on-truncate. The test includes a duplicated comment label in the divergence case, but assertions still cover partial and full truncations.

## Test Signals

Signals are exact replicated storage-space deltas: `-512*4`, `-1536*4`, `-2560*4`, `+1024*4`, `0`, and divergence deltas that reclaim only non-snapshotted current bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTruncateQuotaUpdate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestUpgradeDomainBlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestUpgradeDomainBlockPlacementPolicy.java

## Purpose

`TestUpgradeDomainBlockPlacementPolicy` is an end-to-end test for `BlockPlacementPolicyWithUpgradeDomain` using combined host admin properties and decommission scenarios.

## Important APIs, Types, and Functions

The fixture configures six DataNodes across two racks with upgrade domains, uses `CombinedHostFileManager`, `HostsFileWriter`, `DatanodeAdminProperties`, and sets `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` to `BlockPlacementPolicyWithUpgradeDomain`. Helpers refresh admin properties, create files, wait for replication, and inspect `LocatedBlocks`.

## Control Flow

Setup starts six DataNodes with host/rack mapping, writes admin JSON-like include entries using resolvable DataNode IP/ports, assigns upgrade domains, marks selected nodes decommissioned, refreshes the DataNodeManager, and records expected normal nodes. `testPlacement` writes a replicated file and verifies every block includes required expected normal DataNodes. `testPlacementAfterDecommission` changes which nodes are decommissioned, waits until locations satisfy the new expected set, then calls placement-policy verification.

## State and Persistence Behavior

State lives in the MiniDFSCluster block map, host include file, DataNode admin state, upgrade-domain assignments, and replicated files. File block locations persist until decommission/re-replication changes them.

## Dependencies and Integration Points

It integrates host configuration loading, DataNodeManager refresh, rack awareness, upgrade-domain placement policy, decommissioning, replication, client block-location APIs, and block-placement verification.

## Risks and Edge Cases

Unresolved hostnames are rejected by `CombinedHostFileManager`, so the test uses IPs from actual DataNode IDs. The expected placement sets are based on exact upgrade-domain and rack combinations; changes to policy heuristics can affect assertions.

## Test Signals

Signals include all normal block locations containing required expected DataNode IDs after initial placement, eventual convergence after decommission changes, and `BlockPlacementStatus.isPlacementPolicySatisfied()` for every block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestUpgradeDomainBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestValidateConfigurationSettings.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestValidateConfigurationSettings.java

## Purpose

`TestValidateConfigurationSettings` validates NameNode startup configuration around RPC/HTTP port conflicts and nameservice-specific name-dir keys during format.

## Important APIs, Types, and Functions

The tests use `HdfsConfiguration`, `FileSystem.setDefaultUri`, `DFS_NAMENODE_HTTP_ADDRESS_KEY`, `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_NAMESERVICES`, `DFSTestUtil.formatNameNode`, `NameNode`, `GenericTestUtils.assertExists`, and cleanup through `FileUtil.fullyDeleteContents`.

## Control Flow

The conflict test picks a random high port, configures both RPC default URI and HTTP address to that port, formats the NameNode, and asserts `new NameNode(conf)` throws `BindException`. The non-conflict test retries with distinct random ports and expects startup to succeed. The generic-key test configures `dfs.nameservices=ns1`, sets `dfs.namenode.name.dir.ns1`, formats, asserts the nameservice-specific directory exists, and starts a NameNode using it.

## State and Persistence Behavior

The tests format local NameNode storage directories and bind local network ports. Cleanup removes MiniDFSCluster base directory contents after each test.

## Dependencies and Integration Points

This class covers NameNode HTTP/RPC server startup validation, format-time configuration key resolution, and nameservice-specific key handling.

## Risks and Edge Cases

Randomly selected ports can already be in use; the OK test retries but the conflict test still assumes a free chosen port before the intentional conflict. Format and startup must agree on generic versus nameservice-specific keys.

## Test Signals

Expected signals are `BindException` for matching RPC and HTTP ports, successful NameNode start for distinct ports, existence of the nameservice-specific name dir after format, and successful NameNode start using that dir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestValidateConfigurationSettings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrConfigFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrConfigFlag.java

## Purpose

`TestXAttrConfigFlag` verifies that disabling `dfs.namenode.xattrs.enabled` rejects XAttr client operations while still allowing the NameNode to load existing XAttrs from edit logs and fsimage.

## Important APIs, Types, and Functions

The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `DFS_NAMENODE_XATTRS_ENABLED_KEY`, `NameNodeAdapter.enterSafeMode`, `NameNodeAdapter.saveNamespace`, `IOUtils.cleanupWithLogger`, and JUnit `Executable` for expected failures.

## Control Flow

Operation tests start a formatted cluster with XAttrs disabled, create `/path`, and assert `setXAttr`, `getXAttrs`, and `removeXAttr` throw `IOException` containing the config key. Persistence tests start with XAttrs enabled, create an XAttr, then restart without formatting with XAttrs disabled. One path restarts from edit logs; the other checkpoints first and restarts from fsimage.

## State and Persistence Behavior

The tests persist a namespace path and `user.foo` XAttr through edit logs and optionally fsimage. Restart helper shuts down the old cluster and reuses storage without formatting under a changed config flag.

## Dependencies and Integration Points

It integrates DFSClient XAttr APIs, NameNode XAttr feature flag checks, edit-log replay, fsimage loading, safe mode, and namespace save.

## Risks and Edge Cases

The key distinction is rejecting new XAttr operations while preserving backward-compatible loading of existing metadata. A bug could make disabling XAttrs render a namespace with XAttrs unbootable.

## Test Signals

Signals are `IOException` messages containing `DFS_NAMENODE_XATTRS_ENABLED_KEY` for active operations and successful restarts with disabled XAttrs after both edit-log and fsimage persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrConfigFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrFeature.java

## Purpose

`TestXAttrFeature` verifies in-memory `XAttrFeature` lookup and listing across several XAttr namespaces, empty values, large values, and missing keys.

## Important APIs, Types, and Functions

The test builds `XAttr` instances through `XAttrHelper.buildXAttr`, creates `XAttrFeature` from a mutable list, and calls `getXAttr` and `getXAttrs`. Static data covers `system`, `security`, `trusted`, `user`, and `raw` prefixes plus random 1800- and 2000-byte values and a deterministic 128-byte value.

## Control Flow

The test first asserts an empty feature returns an empty list. It then creates a feature with one XAttr and verifies direct lookup and size. It adds several more XAttrs, recreates the feature, verifies each lookup returns an equal XAttr, verifies the returned list size matches input, confirms every returned item was supplied, and confirms a missing key returns null.

## State and Persistence Behavior

All state is in-memory feature data. It indirectly covers metadata representation that can be serialized in fsimage/edit logs elsewhere.

## Dependencies and Integration Points

This unit test covers the NameNode inode XAttr feature object used by namespace metadata and depends on helper parsing of prefixed XAttr names.

## Risks and Edge Cases

Large XAttr values can stress packing/storage behavior. A feature implementation that drops namespace distinctions, value-less XAttrs, raw namespace entries, or large values would fail lookups.

## Test Signals

Signals include empty-list behavior, equality of every retrieved XAttr, returned list size equal to source list size, membership preservation, and null for `user.a8`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockBenchmarkThroughput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockBenchmarkThroughput.java

## Purpose

`FSNLockBenchmarkThroughput` is a Hadoop `Tool` that benchmarks NameNode throughput under global and fine-grained lock implementations by running a configurable mix of read and write filesystem RPCs.

## Important APIs, Types, and Functions

The class extends `Configured`, implements `Tool`, and wraps a `FileSystem`. Public entry points are `benchmark`, `run`, and `main`. Task builders cover `create`, `addBlock`, `complete`, `append`, `rename`, `delete`, `setPermission`, `setOwner`, `setReplication`, `getFileInfo`, `getListing`, and `getBlockLocation`. It uses `ExecutorService.invokeAll`, `Callable<Void>`, `ThreadLocalRandom`, and synchronized `incOp`.

## Control Flow

`benchmark` creates thirty read files, builds write-heavy and read-heavy callables according to `testingCount` and `readWriteRatio`, shuffles them, runs them with a fixed thread pool of `numClients`, waits for all futures, prints duration and operation counts, then deletes the read files. `run` parses four arguments or prints usage and exits, then invokes `benchmark`.

## State and Persistence Behavior

The benchmark creates and deletes files under the base path and mutates namespace metadata through many concurrent operations. It keeps only in-memory operation counts and does not clean up every transient write path if a task fails before its delete.

## Dependencies and Integration Points

It exercises DFS client and NameNode RPC paths that map to FSNamesystem locks. The paired test configures either `FineGrainedFSNamesystemLock` or `GlobalFSNamesystemLock` and runs this tool against a QJM HA cluster.

## Risks and Edge Cases

This is a stress/benchmark utility, not a deterministic correctness test. High `numClients` and large `testingCount` can overload small test machines. `printUsage` calls `System.exit(1)`, which is risky if used in embedded test contexts with bad args.

## Test Signals

Signals are successful completion of all futures, `ToolRunner.run` returning `0`, printed operation counts, and absence of exceptions under both lock models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockBenchmarkThroughput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFSNLockBenchmarkThroughput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFSNLockBenchmarkThroughput.java

## Purpose

`TestFSNLockBenchmarkThroughput` runs the throughput benchmark against both fine-grained and global FSNamesystem lock providers with several read/write ratios, test counts, and client counts.

## Important APIs, Types, and Functions

The class is tagged `slow`. It uses `MiniQJMHACluster`, `MiniDFSCluster`, `DFS_NAMENODE_LOCK_MODEL_PROVIDER_KEY`, `DFS_HA_TAILEDITS_INPROGRESS_KEY`, `DFS_QJOURNAL_SELECT_INPUT_STREAMS_TIMEOUT_KEY`, `FineGrainedFSNamesystemLock`, `GlobalFSNamesystemLock`, `FSNLockManager`, `ToolRunner`, and `FSNLockBenchmarkThroughput`.

## Control Flow

Each public test delegates to `testBenchmarkThroughput` with a lock model flag and workload parameters. The helper builds a QJM HA cluster with ten DataNodes, transitions NN0 active, obtains a `FileSystem`, constructs benchmark arguments, runs the tool, asserts return code `0`, and shuts down the QJM cluster.

## State and Persistence Behavior

The tests create real HDFS namespace workload under `/tmp/fsnlock/benchmark/throughput` and rely on cluster shutdown for cleanup. HA edit tailing and journal state are active because the benchmark runs in a QJM topology.

## Dependencies and Integration Points

It integrates the benchmark tool, lock model provider selection, QJM shared edits, HA active transition, DFS client operations, and MiniDFSCluster DataNode capacity.

## Risks and Edge Cases

The workloads are large and concurrency-heavy, especially `1000` clients, making the class slow and resource-sensitive. The tests assert success only, not relative throughput.

## Test Signals

Signals are six successful runs: three fine-grained-lock configurations and three global-lock configurations, each returning `0` from `ToolRunner.run`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFSNLockBenchmarkThroughput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFineGrainedFSNamesystemLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFineGrainedFSNamesystemLock.java

## Purpose

`TestFineGrainedFSNamesystemLock` stress-tests `FineGrainedFSNamesystemLock` read/write and interruptible read/write methods for `GLOBAL`, `FS`, and `BM` lock modes under heavy multithreaded use.

## Important APIs, Types, and Functions

The test creates `FineGrainedFSNamesystemLock`, uses `RwLockMode`, `FSNLockManager.writeLock/readLock/writeLockInterruptibly/readLockInterruptibly` and matching unlock methods, `HadoopExecutors.newFixedThreadPool`, `AtomicLong` counters, and many `Callable<Boolean>` tasks.

## Control Flow

`testMultipleThreadsUsingLocks` creates 1000 callables spread across twelve operation categories: normal and interruptible read/write locks for each mode. Each task loops a random 2000-3000 times. Write helpers increment and later decrement a per-mode counter while holding the lock; read helpers only inspect. After invoking all tasks and waiting on futures, the test asserts all counters returned to zero.

## State and Persistence Behavior

Only in-memory lock state and atomic counters are mutated. There is no filesystem persistence.

## Dependencies and Integration Points

This directly tests the lock manager abstraction used by the NameNode fine-grained lock model. Unlock calls include operation names, covering instrumentation-aware unlock signatures.

## Risks and Edge Cases

The test uses Java `assert` statements for final counter checks, so assertions must be enabled to enforce them. Interruptible lock helpers ignore interrupts but carefully retry the decrement if the increment succeeded. The randomized loop count makes runtime variable.

## Test Signals

Signals are completion of all futures within 240 seconds and final `globalCount`, `fsCount`, and `bmCount` equal to zero, showing balanced lock/unlock behavior under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFineGrainedFSNamesystemLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HAStressTestHarness.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HAStressTestHarness.java

## Purpose

`HAStressTestHarness` is a reusable HA test utility that starts a MiniDFS HA cluster and attaches background threads for repeated failover and replication/deletion progress stimulation.

## Important APIs, Types, and Functions

The class owns a `Configuration`, `MiniDFSCluster`, `TestContext`, and configurable NameNode count. It exposes `setNumberOfNameNodes`, `startCluster`, `getFailoverFs`, `addReplicationTriggerThread`, `addFailoverThread`, `startThreads`, `stopThreads`, and `shutdown`. It uses `MiniDFSNNTopology.simpleHATopology`, `RepeatingTestThread`, `DataNodeTestUtils`, and `BlockManagerTestUtil.computeAllPendingWork`.

## Control Flow

The constructor sets small block size, short heartbeat/tail-edits periods, and high replication stream limits. `startCluster` builds an HA cluster with three DataNodes. Replication trigger threads periodically force deletion reports, heartbeats, and pending block work computation. Failover threads transition each NameNode to standby and the next to active in a ring, sleeping between cycles.

## State and Persistence Behavior

The harness mutates cluster HA role state and DataNode/BlockManager transient work queues. It does not create files itself, but tests using it typically persist namespace and block state while background activity runs.

## Dependencies and Integration Points

It integrates MiniDFSCluster HA topology, failover client configuration through `HATestUtil`, DataNode test hooks, block manager scheduling, and multithreaded test utilities.

## Risks and Edge Cases

The failover loop assumes node indices are valid and transitions are legal in sequence. Background threads can mask or expose races depending on interval choices. `shutdown` must stop threads before cluster teardown to avoid touching closed services.

## Test Signals

Consumers should observe no exceptions from `TestContext`, successful failover cycles, accelerated deletion/replication progress, and clean shutdown with all test threads stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HAStressTestHarness.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HATestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HATestUtil.java

## Purpose

`HATestUtil` centralizes static helpers for HDFS HA tests: standby catch-up waits, deletion waits, failover filesystem configuration, observer-read cluster setup, proxy inspection, checkpoint waits, and observer alignment-context state manipulation.

## Important APIs, Types, and Functions

Key methods include `waitForStandbyToCatchUp`, `waitForDNDeletions`, `waitForNNToIssueDeletions`, `configureFailoverFs`, `configureObserverReadFs`, `isSentToAnyOfNameNodes`, `setUpObserverCluster`, many `setFailoverConfigurations` overloads, `setupHAConfiguration`, `getLogicalHostname`, `getLogicalUri`, `waitForCheckpoint`, `setACStateId`, and `getLastSeenStateId`. It defines `CouldNotCatchUpException`.

## Control Flow

Catch-up helpers roll or poll edit logs until standby txid or deletion counters reach target values. Failover configuration helpers enumerate MiniDFSCluster NameNodes, write logical nameservice keys, RPC addresses, HA NameNode IDs, proxy provider class names, and `fs.defaultFS`. Observer setup builds a QJM HA cluster with active, standby, and observer nodes, with optional fast tailing. Proxy helpers use Java reflection/proxy APIs to inspect `RetryInvocationHandler` and `ObserverReadProxyProvider`.

## State and Persistence Behavior

The utility mutates Hadoop `Configuration`, MiniDFSCluster HA states, observer state, and client alignment context. Reflection helpers directly reset `ClientGSIContext.lastSeenStateId`.

## Dependencies and Integration Points

It is a core support layer for HA, QJM, observer-read, failover, DataNode deletion, checkpoint, and client state-ID tests. It integrates with `DFSUtil`, `HdfsClientConfigKeys`, `ConfiguredFailoverProxyProvider`, `ObserverReadProxyProvider`, `MiniQJMHACluster`, and `FSImageTestUtil`.

## Risks and Edge Cases

Timeout values encode assumptions about tailing and deletion progress. Reflection against private fields can break on implementation changes. Overloaded configuration methods must keep generated HA keys consistent with client expectations.

## Test Signals

Signals include successful failover client creation, expected last proxy target detection, observer cluster role setup, checkpoint txid visibility, deletion counters reaching zero, and explicit `CouldNotCatchUpException` when standby lag exceeds timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HATestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapAliasmap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapAliasmap.java

## Purpose

`TestBootstrapAliasmap` verifies that a provided-storage in-memory LevelDB aliasmap can be downloaded from a NameNode and started from the downloaded directory with the same block pool ID and entries.

## Important APIs, Types, and Functions

The setup calls `MiniDFSCluster.setupNamenodeProvidedConfiguration`, assigns a free aliasmap RPC port, and starts a one-DataNode cluster. The test uses `InMemoryLevelDBAliasMapServer`, `Block`, `ProvidedStorageLocation`, `TransferFsImage.downloadAliasMap`, `DFSUtil.getInfoServerWithDefaultHost`, and a new server constructed with `InMemoryAliasMap::init`.

## Control Flow

The test writes two block-to-location mappings into the running NameNode aliasmap server, downloads the aliasmap over the NameNode HTTP image-transfer path into a fresh directory, configures a second aliasmap server to use that directory and a free RPC address, starts it, then lists and reads mappings.

## State and Persistence Behavior

Aliasmap entries are persisted in the LevelDB directory copied by `downloadAliasMap`. The test also verifies the block pool ID survives into the new server.

## Dependencies and Integration Points

It integrates provided storage configuration, aliasmap RPC/server lifecycle, NameNode HTTP transfer, LevelDB-backed aliasmap persistence, and block pool identity.

## Risks and Edge Cases

The test assumes the HTTP endpoint transfers a complete aliasmap snapshot and that the new server can start independently from the copied directory. Free port selection avoids default port conflicts.

## Test Signals

Signals are exactly two listed file regions, non-null reads for both blocks, and `newServer.getBlockPoolId()` equal to the source NameNode block pool ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapAliasmap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandby.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandby.java

## Purpose

`TestBootstrapStandby` validates `BootstrapStandby` against a three-NameNode HA topology with file-based shared edits, covering successful bootstraps, later checkpoints, rolling upgrade rollback images, missing shared edits, preformatted dirs, non-active source nodes, and bootstrap-specific transfer throttling.

## Important APIs, Types, and Functions

The fixture builds a custom `MiniDFSNNTopology`, keeps NN0 active, shuts down other NameNodes, and uses `BootstrapStandby.run`, `FSImageTestUtil`, `NameNodeAdapter`, `CheckpointSignature`, `NNStorage`, `NameNodeLayoutVersion`, `RollingUpgradeAction`, `DistributedFileSystem`, `LogCapturer`, Mockito spies, and `SubjectInheritingThread`.

## Control Flow

Tests delete standby name dirs, confirm startup fails before bootstrap, run bootstrap with `-nonInteractive` or `-force`, verify copied checkpoint txids, and restart standbys. Later-checkpoint tests roll logs and save namespace before bootstrapping. Rolling-upgrade tests spoof future layout versions, ensure invalid-version handling before upgrade, prepare rolling upgrade, copy both normal and rollback images, restart with rolling-upgrade args, and then verify failure modes. Missing-log tests delete a shared finalized edits segment and expect `ERR_CODE_LOGS_UNAVAILABLE`. Rate throttling compares global image-transfer rate with bootstrap-specific rate.

## State and Persistence Behavior

The tests mutate local NameNode storage dirs, shared edits directories, fsimage checkpoints, rollback images, `seen_txid`, rolling-upgrade state, and transfer-rate config. They directly delete directories and edit-log segments to create failure scenarios.

## Dependencies and Integration Points

It integrates HA bootstrap, HTTP image transfer, shared edits validation, checkpoint signatures, rolling upgrade, fsimage rollback handling, configuration of transfer throttles, and MiniDFSCluster restart semantics.

## Risks and Edge Cases

Bootstrapping from stale or incomplete shared edits can create unusable standbys. Rolling upgrades require version compatibility and rollback image transfer. Existing directories must be rejected unless forced. Throttling behavior must use the bootstrap-specific key to avoid global transfer settings breaking bootstrap.

## Test Signals

Signals include return code `0` for valid bootstrap, `ERR_CODE_INVALID_VERSION`, `ERR_CODE_LOGS_UNAVAILABLE`, and `ERR_CODE_ALREADY_FORMATTED` for specific failures, matching NN files after bootstrap, unchanged shared `seen_txid`, rollback checkpoints present during rolling upgrade, and expected timeout only when the bootstrap-specific rate is too low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandby.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithInProgressTailing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithInProgressTailing.java

## Purpose

`TestBootstrapStandbyWithInProgressTailing` specializes the QJM bootstrap-standby tests to verify bootstrap works when in-progress edit tailing is enabled but RPC tailing is limited to one transaction per call.

## Important APIs, Types, and Functions

The class extends `TestBootstrapStandbyWithQJM` and overrides `createConfig`. It sets `DFS_HA_TAILEDITS_INPROGRESS_KEY=true` and `dfs.ha.tail-edits.qjm.rpc.max-txns=1`.

## Control Flow

All inherited QJM bootstrap tests run with the overridden configuration. This forces bootstrap tailing to retrieve in-progress edits through multiple small RPC calls instead of one large call.

## State and Persistence Behavior

State behavior is inherited from the QJM tests: NameNode storage, QJM journal edits, and upgrade directories are created and bootstrapped. The only local mutation is configuration.

## Dependencies and Integration Points

It specifically integrates `BootstrapStandby`, QJM in-progress edit tailing, and the per-RPC max transaction limit introduced for tailing.

## Risks and Edge Cases

If bootstrap assumes all required in-progress edits fit in one RPC, inherited tests fail under this configuration. The class has no tests of its own, so coverage depends entirely on inherited methods.

## Test Signals

Signals are inherited test success under one-transaction tailing: standbys bootstrap from active or standby QJM sources and upgrade-related bootstrap flows still pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithInProgressTailing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithQJM.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithQJM.java

## Purpose

`TestBootstrapStandbyWithQJM` validates `BootstrapStandby` when HA shared edits are stored in JournalNodes, including bootstrapping from active and standby sources and preserving upgrade state.

## Important APIs, Types, and Functions

The class uses `MiniQJMHACluster`, `MiniJournalCluster`, `MiniDFSCluster`, `BootstrapStandby.run`, `HATestUtil.configureFailoverFs`, `FSImageTestUtil`, `NNStorage`, `FSImage`, `Whitebox`, and an `UpgradeState` enum with `NORMAL`, `RECOVER`, and `FORMAT`.

## Control Flow

Setup builds a three-NameNode QJM HA cluster, transitions NN0 active, and writes `/test2` to generate in-progress edits. Bootstrap tests transition NN0 standby or active, shut down NN1/NN2, run bootstrap with `-force`, and verify checkpoints and file matches. Upgrade tests mark NN0's `FSImage.isUpgradeFinalized=false`, optionally rename NN1 current dir to `previous.tmp` or an unrelated path, run bootstrap, verify namespace files match, restart NN1, and assert NN1 remains in upgrade state.

## State and Persistence Behavior

The tests persist namespace edits in QJM, NameNode local storage, checkpoint image files, and upgrade `previous` directories. RECOVER and FORMAT scenarios directly rename local storage directories.

## Dependencies and Integration Points

It integrates QJM shared edits, BootstrapStandby namespace copy, failover filesystem configuration, NameNode startup recovery/format handling, and upgrade directory creation.

## Risks and Edge Cases

Bootstrapping from QJM must include in-progress edits and work whether the source NN is active or standby. Upgrade bootstrap must recover `previous.tmp` or format missing/unformatted dirs before entering upgrade state.

## Test Signals

Signals include bootstrap return code `0`, checkpoints containing txid `0`, `FSImageTestUtil.assertNNFilesMatch`, and restarted NN1 reporting upgrade not finalized in all three upgrade-state scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithQJM.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestConsistentReadsObserver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestConsistentReadsObserver.java

## Purpose

`TestConsistentReadsObserver` verifies observer-read consistency semantics for HDFS ObserverNode clients, including `msync`, automatic msync, requeue/backoff, new-client alignment, uncoordinated calls, non-observer proxy rejection, FileContext support, and RPC queue metrics.

## Important APIs, Types, and Functions

The suite starts a QJM HA cluster with one observer through `HATestUtil.setUpObserverCluster`, with state context enabled and fast tailing disabled. It uses `ObserverReadProxyProvider`, `DistributedFileSystem.msync`, `FileContext.msync`, `HATestUtil.isSentToAnyOfNameNodes`, `NameNodeAdapter`, `RpcScheduler`, `Schedulable`, `RemoteException`, `StandbyException`, metrics assertions, and a nested `TestRpcScheduler`.

## Control Flow

Most tests perform a write on the active, then issue reads expected to block or requeue until the observer tails edits. Explicit and auto-msync tests use a second client with cache disabled and verify reads go to the observer only after state ID alignment. New-client tests reorder HA roles so a new client must contact active before observer. Uncoordinated-call tests show `datanodeReport` bypasses coordinated waiting while `getFileInfo` blocks. Non-observer proxy tests configure a plain failover provider pointed at the observer and expect `StandbyException`. Metrics tests compare queue and processing operation counters after a blocked read completes.

## State and Persistence Behavior

The tests mutate namespace directories, HA roles, observer edit-tail state, client alignment-context state, observer RPC call queue configuration, and metrics counters. Cleanup deletes the test path after each test.

## Dependencies and Integration Points

It integrates ObserverNode state IDs, client-side observer proxy selection, edit log rolling/tailing, RPC backoff, FileSystem and FileContext APIs, HA role transitions, and metrics.

## Risks and Edge Cases

Observer reads must never return stale results relative to the client's last seen state. Auto-msync period handling can make tests time-sensitive. Requeue/backoff must eventually fail over to active when observer cannot catch up. Non-observer-aware clients must be rejected by observers.

## Test Signals

Signals include reads blocking before `rollEditLogAndTail` and succeeding afterward, last proxy indices matching active or observer expectations, `TimeoutException` for effectively disabled auto-msync, fast uncoordinated `datanodeReport`, `StandbyException` for plain provider requests, successful FileContext read after msync, and equal `RpcQueueTimeNumOps` and `RpcProcessingTimeNumOps`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestConsistentReadsObserver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDFSUpgradeWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDFSUpgradeWithHA.java

## Purpose

`TestDFSUpgradeWithHA` validates HDFS upgrade, finalize, rollback, and second-NameNode restrictions in HA deployments using both NFS-style shared edits and QJM JournalNodes.

## Important APIs, Types, and Functions

The fixture uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `MiniQJMHACluster`, `StartupOption.UPGRADE/REGULAR`, `BootstrapStandby`, `DFSAdmin.finalizeUpgrade`, `NameNode.doRollback`, `Journal`, `BestEffortLongFile`, `PersistentLongFile`, `Whitebox`, and helper methods for checking `previous` directories, cTimes, and committed transaction IDs.

## Control Flow

Tests start HA clusters, transition NN0 active, perform filesystem operations, shut down NN1, restart NN0 with `-upgrade`, verify `previous` directories in NN and shared/JN storage, continue writing, restart regular, bootstrap NN1, fail over, finalize, or roll back. QJM tests additionally inspect `committedTxnId` before, during, and after upgrade/rollback. One test ensures finalization fails when no NN is active. Another simulates `previous.tmp` dirs and asserts restart succeeds. The final test verifies a second NameNode cannot independently start with `-upgrade` after shared logs are already upgraded.

## State and Persistence Behavior

The suite heavily mutates persistent NameNode storage, shared edits directories, JournalNode directories, `previous` and `previous.tmp` directories, cTime metadata, committed transaction ID files, and namespace directories. Rollback tests shut down NameNodes while leaving storage or JournalNodes to verify disk state transitions.

## Dependencies and Integration Points

It integrates HA startup options, shared edits upgrade markers, JournalNode epoch/committed-txid persistence, DFSAdmin finalize workflow, bootstrap standby after upgrade, rollback commands, failover filesystem configuration, and NameNode storage recovery.

## Risks and Edge Cases

HA upgrades require exactly one initiator, consistent cTimes across NameNodes, preserved JournalNode epoch files, and safe finalize only when an active NN can coordinate. Rollback must reset committed txid without regressing below pre-upgrade state. Starting a second NN with `-upgrade` against already upgraded shared logs must be rejected.

## Test Signals

Signals include expected presence/absence of `previous` directories, equal cTimes, successful writes before and after upgrade/failover, bootstrap return code `0`, `Cannot finalize with no NameNode active`, JournalNode committed txid monotonicity/reset assertions, no `previous` dirs after finalize or rollback, and an `IOException` mentioning shared log already being upgraded when a second NN uses `-upgrade`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDFSUpgradeWithHA.java -->
