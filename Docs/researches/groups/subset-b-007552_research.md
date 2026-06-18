# subset-b-007552 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsck.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsck.java

**Purpose:** Broad JUnit 5 integration coverage for HDFS `DFSck`/`NamenodeFsck`. It validates fsck command status, output formatting, permission handling, corrupt/missing block accounting, repair options, snapshot handling, block-id inspection, erasure-coded files, decommission/maintenance states, storage policies, and audit logging.

**Important APIs and flow:** `runFsck()` wraps `ToolRunner.run(new DFSck(conf, out), args)` and captures command output while checking return codes. The class builds many `MiniDFSCluster` instances, creates files with `DFSTestUtil`, talks to the NN through `DFSClient`, `NamenodeProtocols`, and `NameNodeRpcServer`, and checks strings from `NamenodeFsck` such as `HEALTHY_STATUS`, `CORRUPT_STATUS`, and block-state statuses. `CorruptedTestFile` caches original bytes, deletes or overwrites block files in DataNode storage, and verifies `-move` salvage under `/lost+found`.

**Control flow:** Each test constructs a specific filesystem state, runs fsck with flags such as `-move`, `-delete`, `-files`, `-blocks`, `-locations`, `-replicaDetails`, `-openforwrite`, `-list-corruptfileblocks`, `-includeSnapshots`, `-blockId`, `-maintenance`, `-storagepolicies`, and `-upgradedomains`, then asserts return codes and output. Several tests poll with `GenericTestUtils.waitFor()` until block reports, corrupt-replica records, decommission, maintenance, or unrecoverable EC block-group state is visible to the NameNode.

**State and persistence behavior:** Tests mutate actual MiniDFS block files to simulate missing or corrupt replicas, disable immediate corrupt-block deletion in setup, restart NameNodes to check no-DataNode corruption reporting, and inspect access times to ensure fsck does not update atime. Snapshot tests verify inclusion/exclusion of `.snapshot` paths. HA and EC tests validate fsck behavior across failover, striped block groups, redundant internal blocks, under-construction EC files, and corrupt/missing EC data.

**Dependencies and integration points:** Depends heavily on `MiniDFSCluster`, `DFSck`, `NamenodeFsck`, `DFSTestUtil`, `FSNamesystem`, `BlockManager`, `DatanodeManager`, `HostsFileWriter`, EC helpers, audit logging, and HDFS client protocols. It crosses CLI, RPC, NN metadata, DN storage, block placement, maintenance/decommission administration, and JMX/audit-adjacent behavior.

**Risks and test signals:** The tests are slow and timing-sensitive because block reports, redundancy monitors, stale-node detection, and maintenance/decommission transitions are asynchronous. They rely on exact fsck text, so output wording changes can break tests. Passing signals that fsck reports health accurately, preserves access times, handles permissions, reports replica and EC states correctly, salvages or deletes corrupt files as expected, and respects privileged access for listing corrupt blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsckWithMultipleNameNodes.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsckWithMultipleNameNodes.java

**Purpose:** Verifies fsck works against federated HDFS deployments with multiple NameNodes and also through `viewfs` mount links.

**Important APIs and flow:** `createConf()` builds an `HdfsConfiguration` with short access-time precision and block-report intervals. `runTest()` creates a `MiniDFSCluster` using `MiniDFSNNTopology.simpleFederatedTopology(nNameNodes)`, applies `DFSTestUtil.setFederatedConfiguration()`, then uses a `Suite` helper to create one file per namespace through each namespace-specific `FileSystem`.

**Control flow:** The single test calls `runTest(3, 1, conf)`. For each NameNode namespace, the test creates `/tmp.txt`, waits for replication, invokes `TestFsck.runFsck()` on the fully qualified HDFS URL, and expects `Status: HEALTHY`. It then adds `viewfs` links with `ConfigUtil.addLink()` and repeats fsck against `viewfs:/mount/nn_i/tmp.txt`.

**State and persistence behavior:** State is limited to the MiniDFS federated namespace and the client-side `viewfs` configuration. No restart or edit-log replay is tested. The test does verify that each namespace's independent file can be resolved and checked without confusing the default filesystem or another NameNode namespace.

**Dependencies and integration points:** Integrates `DFSck` with federated `MiniDFSCluster`, `ClientProtocol`, `DFSTestUtil`, and `viewfs` link resolution. It also reuses `TestFsck.runFsck()` for output capture and return-code handling.

**Risks and test signals:** The assertions check text rather than structured status. The test uses one DataNode and replication derived as `max(1, nDataNodes - 1)`, so it is focused on routing/namespace selection rather than redundancy. A pass signals that fsck can target explicit HDFS namespace URIs and `viewfs` links in a multi-NameNode configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsckWithMultipleNameNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGenericJournalConf.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGenericJournalConf.java

**Purpose:** Tests generic edit-log journal plugin configuration for NameNode startup, including missing plugin mappings, invalid classes, bad constructors, and successful custom `JournalManager` initialization.

**Important APIs and flow:** Tests set `DFS_NAMENODE_EDITS_DIR_KEY` to `dummy://test` and configure `DFS_NAMENODE_EDITS_PLUGIN_PREFIX + ".dummy"` as needed. They start `MiniDFSCluster` with zero DataNodes and assert startup throws `IllegalArgumentException` or succeeds. `DummyJournalManager` implements `JournalManager` and records constructor parameters plus calls to `format()` and `hasSomeData()`.

**Control flow:** `testNotConfigured()` expects a dummy URI without a plugin class to fail. `testClassDoesntExist()` points the dummy scheme at a nonexistent class and expects failure. `testBadConstructor()` configures a class without the required `(Configuration, URI, NamespaceInfo)` constructor and checks the error contains "Unable to construct journal". `testDummyJournalManager()` configures the valid dummy manager, starts the NameNode, and verifies URI, configuration, namespace info, cluster ID, prompt, and format calls.

**State and persistence behavior:** The test does not persist real edits in the dummy journal; `startLogSegment()` returns a mocked `EditLogOutputStream`. Persistent behavior under test is the NameNode formatting/startup path choosing edit directories and consulting journal metadata through `hasSomeData()` and `format()`.

**Dependencies and integration points:** Integrates `MiniDFSCluster`, `DFSConfigKeys`, `JournalManager`, `NamespaceInfo`, `Storage`, `StorageInfo`, and reflection-based plugin construction. Mockito supplies the output stream stub.

**Risks and test signals:** `DummyJournalManager` stores static state and does not reset it between tests, so additional tests must avoid stale-state assumptions. Passing signals that journal plugin lookup fails clearly for bad config and that valid plugins receive the expected constructor context and lifecycle callbacks during NameNode format/startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGenericJournalConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetBlockLocations.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetBlockLocations.java

**Purpose:** Unit-level coverage for `FSNamesystem.getBlockLocations()` when paths are addressed through `/.reserved/.inodes/<id>`, especially atime edit logging under delete and rename races.

**Important APIs and flow:** `setupFileSystem()` constructs an `FSNamesystem` with mocked `FSImage` and `FSEditLog`, creates an `INodeFile` with a known inode ID, and inserts it into `FSDirectory` under `/foo`. Tests call `fsn.getBlockLocations("dummy", RESERVED_PATH, 0, 1024)` and use Mockito verification on `editlog.logTimes()`.

**Control flow:** `testResolveReservedPath()` verifies the reserved inode path is resolved to `/foo` before logging access times. `testGetBlockLocationsRacingWithDelete()` spies `FSNamesystem.checkOperation(WRITE)` to delete the file just before the real operation proceeds, then asserts atime is not logged for a deleted inode. `testGetBlockLocationsRacingWithRename()` similarly renames `/foo` to `/bar` and asserts atime logging uses `/bar`.

**State and persistence behavior:** The mocked edit log is the persistence signal: `logTimes(path, mtime, atime)` is expected only when the inode still exists and with the post-resolution path after rename. The in-memory namespace is mutated under FS or global write locks to model racing metadata changes.

**Dependencies and integration points:** Integrates `FSNamesystem`, `FSDirectory`, `FSDirDeleteOp`, `FSDirRenameOp`, `INodesInPath`, `INodeFile`, edit-log atime logging, and reserved inode path resolution. Mockito spies are used to inject races at operation-category checks.

**Risks and test signals:** The race is synthetic and depends on the current placement of `checkOperation(WRITE)` inside `getBlockLocations()`. A pass signals reserved inode paths resolve before atime persistence, deletes suppress stale atime edits, and renames persist access-time updates under the current canonical path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetBlockLocations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetContentSummaryWithPermission.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetContentSummaryWithPermission.java

**Purpose:** Tests permission enforcement for NameNode `getContentSummary()` over directories and files.

**Important APIs and flow:** `setUp()` starts a `MiniDFSCluster` with block size `1024` and three DataNodes, then stores a `DistributedFileSystem`. `verifySummary()` asserts directory count, file count, and byte length. Tests call `cluster.getNameNodeRpc().getContentSummary(path)` directly and also as a non-superuser through `UserGroupInformation.doAs()`.

**Control flow:** `testGetContentSummarySuperUser()` builds `/fooSuper/barSuper/bazSuper`, creates a 10-byte file, and verifies the superuser can read the same summary even after permissions on the root directory, subdirectory, and file are set to `000`. `testGetContentSummaryNonSuperUser()` builds a similar tree, verifies default `755` directories and `644` file allow summary, then denies summary by removing access from the root directory and subdirectory. It restores directory permissions to `READ_EXECUTE` and confirms file permissions do not affect directory summary traversal.

**State and persistence behavior:** The persistent state is HDFS namespace metadata: directory/file permissions, file length, and content summary counters. No restart is performed. The tests focus on runtime permission checks, not edit-log replay.

**Dependencies and integration points:** Integrates `MiniDFSCluster`, `DistributedFileSystem`, `NameNodeRpcServer.getContentSummary()`, `DFSTestUtil.createFile()`, `FsPermission`, `FsAction.READ_EXECUTE`, and HDFS access-control exceptions.

**Risks and test signals:** The expected behavior is nuanced: directories require read and execute access for non-superusers, but file mode bits inside the tree do not block summary. Passing signals that superuser bypass works, non-superusers are constrained by traversed directories, and content-summary counts remain correct under permission changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetContentSummaryWithPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetImageServlet.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetImageServlet.java

**Purpose:** Unit coverage for `ImageServlet.isValidRequestor()`, which authorizes HTTP fsimage/edits transfer requestors in secure HA NameNode deployments.

**Important APIs and flow:** The test creates an `HdfsConfiguration`, installs simple Kerberos short-name rules, configures nameservice `ns1` with HA NameNodes `nn1` and `nn2`, and sets NN RPC addresses and Kerberos principals. `NameNode.initializeGenericKeys(conf, "ns1", "nn1")` makes the configuration look like NN1. A mocked `ServletContext` returns a mocked `AccessControlList` from `HttpServer2.ADMINS_ACL`.

**Control flow:** With ACL initially denying all users, the test asserts `hdfs/host2@TEST-REALM.COM` is still a valid requestor because it corresponds to the peer HA NameNode. It then marks short user `atm` as an admin, verifies the peer NN remains valid, verifies `atm@TEST-REALM.COM` is valid, and verifies unrelated `todd@TEST-REALM.COM` is rejected.

**State and persistence behavior:** There is no filesystem or persistent state. The tested state is configuration-derived Kerberos principal mapping plus servlet-context ACL lookup.

**Dependencies and integration points:** Integrates `ImageServlet`, `DFSUtil.addKeySuffixes()`, HA NameNode config keys, `KerberosName`, `UserGroupInformation`, `AccessControlList`, `HttpServer2.ADMINS_ACL`, and Mockito.

**Risks and test signals:** The test depends on principal host substitution and Kerberos short-name rules matching current implementation. Passing signals fsimage transfer authorization admits HA peer NameNodes independently of admin ACLs, admits configured administrators, and rejects ordinary users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetImageServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHAWithInProgressTail.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHAWithInProgressTail.java

**Purpose:** Tests HA failover when standby NameNode tails in-progress edit-log segments from a Quorum Journal Manager and one JournalNode gives empty or slow responses.

**Important APIs and flow:** `startUp()` enables `DFS_HA_TAILEDITS_INPROGRESS_KEY`, shortens `DFS_QJOURNAL_SELECT_INPUT_STREAMS_TIMEOUT_KEY`, enables standby reads with `HAUtil.setAllowStandbyReads()`, and starts `MiniQJMHACluster`. The test keeps references to the DFS cluster, journal cluster, and both NameNodes.

**Control flow:** `testFailoverWithAbnormalJN()` transitions NN0 active, stops NN1's `EditLogTailer`, creates a directory through NN0, transitions NN0 standby, then replaces NN1's edit log with a Mockito spy. The spy intercepts `recoverUnclosedStreams()` and calls `spyOnJASjournal()` to replace the `JournalManager` with a spying `QuorumJournalManager` whose one JournalNode has empty/slow responses. NN1 is transitioned active and must still serve `getFileInfo()` for the directory created by NN0.

**State and persistence behavior:** The state under test is edit-log durability in QJM and the standby's ability to recover and tail unfinalized segments during failover. The filesystem mutation is a single mkdir that must become visible on the new active.

**Dependencies and integration points:** Integrates HA transition APIs, `MiniQJMHACluster`, `MiniJournalCluster`, `QuorumJournalManager`, `JournalSet.JournalAndStream`, `FSEditLog.recoverUnclosedStreams()`, `EditLogTailer`, and `SpyQJournalUtil`.

**Risks and test signals:** The test is sensitive to QJM timing and internal journal-set structure. A pass signals failover catch-up can survive an abnormal JournalNode while reading in-progress segments, preventing metadata loss during active transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHAWithInProgressTail.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHDFSConcat.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHDFSConcat.java

**Purpose:** Integration tests for HDFS `concat`, covering block transfer into the target inode, source deletion, content ordering, edit-log replay, quota accounting, path validation, reserved paths, snapshots/inode references, and permission enforcement.

**Important APIs and flow:** `startUpCluster()` creates a two-DataNode `MiniDFSCluster` with 512-byte block size, exposes `DistributedFileSystem` and `NamenodeProtocols`, and teardown closes both. Tests create files with `DFSTestUtil`, call `dfs.concat(target, sources)`, inspect `HdfsFileStatus`, `LocatedBlocks`, `ContentSummary`, and exceptions, and sometimes use alternate `UserGroupInformation` filesystems.

**Control flow:** `testConcat()` concatenates ten full files and one small file, verifies block count, length, source removal, recreated source names, and byte ordering. `testConcatInEditLog()` restarts the NameNode and checks replay preserves target existence and modification time. Negative tests cover different directories, nonexistent sources, empty source lists, larger preferred source block size, reserved raw paths, same source/target inode reference, permission enabled/disabled behavior, and separate read/write permission failures. Quota tests verify concat may decrease or increase consumed space depending on source/target replication and can throw `QuotaExceededException`.

**State and persistence behavior:** Concat mutates namespace state by moving source blocks into the target inode and deleting source inodes; edit-log replay is explicitly checked. Quota namespace and disk-space counts are expected to update atomically with the concat. Snapshot/reference coverage ensures source-target identity checks are based on inode identity, not only path text.

**Dependencies and integration points:** Integrates `DistributedFileSystem.concat()`, NN RPCs, `FSDirectory`, edit logs, block locations, quotas, snapshots, `RemoteException`, `AccessControlException`, and permission configuration (`DFS_PERMISSIONS_ENABLED_KEY`).

**Risks and test signals:** Concat is sensitive to block layout and quota math. Passing signals the user-visible API preserves byte order, removes sources, persists across restart, rejects invalid path/layout cases, and enforces permissions and quotas consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHDFSConcat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHostsFiles.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHostsFiles.java

**Purpose:** Parameterized tests for NameNode include/exclude host-file handling through both `HostFileManager` and `CombinedHostFileManager`.

**Important APIs and flow:** The class is a JUnit parameterized class over host file manager implementation. `getConf()` creates an `HdfsConfiguration` with fast heartbeats, redundancy, pending-reconstruction, and block-report intervals; rack awareness enabled through a topology script key; and `DFS_NAMENODE_HOSTS_PROVIDER_CLASSNAME_KEY` set to the current manager class. `HostsFileWriter` writes include/exclude files for refresh.

**Control flow:** `testHostsExcludeInUI()` creates a four-DataNode, two-rack cluster, writes a replicated file, excludes a DataNode holding a replica, calls `refreshNodes()`, waits for decommission and replication, then checks the `NameNodeInfo` JMX `LiveNodes` JSON contains `Decommissioned`. `testHostsIncludeForDeadCount()` starts zero DataNodes with two include entries and asserts NameNode and JMX dead/live counts. `testNewHostAndExcludeFile()` starts with two included dead hosts, then refreshes with a new hosts file containing a third host and verifies dead count increases.

**State and persistence behavior:** State lives in host include/exclude files, DataNode admin state, NameNode live/dead/decommission counters, block placement, and JMX attributes. No restart is tested; behavior is driven by `refreshNodes()`.

**Dependencies and integration points:** Integrates `HostsFileWriter`, `DatanodeManager.refreshNodes()`, host config manager implementations, block replication, decommission state, rack-aware placement, `FSNamesystem` counters, and NameNode JMX MBeans.

**Risks and test signals:** Tests are timing-sensitive around decommission and replication. Passing for both managers signals host-file parsing and refresh semantics are consistent, decommission appears in UI/JMX, and configured-but-absent hosts count as dead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHostsFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeAttributeProvider.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeAttributeProvider.java

**Purpose:** Tests the NameNode `INodeAttributeProvider` extension point: lifecycle, attribute substitution, ACL/XAttr substitution, external permission enforcement, bypass users, content-summary authorization, subclassed access exceptions, and renamed snapshot paths.

**Important APIs and flow:** `setUp()` configures `DFS_NAMENODE_INODE_ATTRIBUTES_PROVIDER_KEY` with `MyAuthorizationProvider`, enables ACLs, configures bypass users `u2` and `u3`, skips edit-log fsync for testing, and starts `MiniDFSCluster`. The provider records calls in static `CALLED`, starts/stops lifecycle hooks, returns wrapped `INodeAttributes`, and installs `MyAccessControlEnforcer`.

**Control flow:** Provider attributes are default except paths containing `authz`, where owner/group become `foo`/`bar`, permission becomes `0770`, ACL includes group `xxx:ALL`, and XAttr `user.test` is exposed. Tests verify provider calls for mkdir/list/getAclStatus, non-bypass and bypass behavior, file status for superuser and normal user, null ACL feature behavior under `/user/acl`, ACL status returning provider owner/group/perms, normalized `AccessControlException` when a subclass is thrown, content summary using provider permissions, and snapshot diff after rename/delete sequences.

**State and persistence behavior:** Underlying HDFS permissions and provider-visible attributes can intentionally differ. Tests do not restart, so provider state is runtime-only, but namespace mutations include directories, files, snapshots, renames, and deletes. Teardown asserts the provider `stop()` lifecycle was called.

**Dependencies and integration points:** Integrates `INodeAttributeProvider`, `AccessControlEnforcer`, `AuthorizationContext`, `FSPermissionChecker`, ACL and XAttr APIs, `UserGroupInformation`, snapshots, and `DistributedFileSystem`.

**Risks and test signals:** Static flags (`runPermissionCheck`, `shouldThrowAccessException`) require cleanup discipline. Passing signals external authorization can override visible inode metadata and permission checks while bypass users retain raw HDFS metadata, and that snapshot/rename path reconstruction remains compatible with the provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeAttributeProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeFile.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeFile.java

**Purpose:** Unit and MiniDFS integration coverage for `INodeFile`, inode IDs, reserved inode paths, path resolution, listing pagination limits, under-construction state, XAttrs, block clearing, and concat quota accounting.

**Important APIs and flow:** Helper constructors build contiguous and striped `INodeFile` objects with `PermissionStatus`; `createINodeFiles()` creates inodes with one `BlockInfoContiguous`; `getInodePath()` builds `/.reserved/.inodes/<id>/...` paths. Tests use both direct in-memory inode objects and real `MiniDFSCluster` operations through `DistributedFileSystem`, `DFSClient`, and `NamenodeProtocols`.

**Control flow:** Constructor tests validate storage-policy ID bounds, replication/preferred-block-size bounds, contiguous-vs-striped redundancy arguments, full path construction, block type, `valueOf()` casting, concat of in-memory block arrays, under-construction transitions, XAttr feature add/remove, and `clearBlocks()`. Cluster tests verify parent pointers after quota replacement and rename, inode ID allocation/map size through create/rename/delete/concat/restart/saveNamespace/open-file cases, writes to deleted files fail, reserved inode paths work for create/status/permission/owner/times/replication/ACL/XAttrs/access/append/lease/block-locations/rename/content-summary/list/delete, reserved names cannot be created or loaded, and `..` under inode paths resolves correctly. Listing tests check location-count limits and inode-path startAfter behavior, including deleted startAfter exceptions.

**State and persistence behavior:** This file explicitly checks edit-log/fsimage persistence for inode IDs and reserved-name validation across restart, plus namespace state after quota node replacement. It also validates runtime inode-map replacement when quota is set/unset and quota usage after concat.

**Dependencies and integration points:** Integrates `INodeFile`, `INodeDirectory`, `FSDirectory`, `FSNamesystem`, `INodeId`, `Snapshot`, `BlockManager`, reserved path resolution, symlink rules, quotas, listing RPCs, XAttrs, ACLs, and HDFS client operations.

**Risks and test signals:** Tests touch internal constants and static `FSDirectory.CHECK_RESERVED_FILE_NAMES`, so cleanup matters. Passing signals inode bit-field constraints, parent/inode-map consistency, reserved inode path support, edit-log/fsimage inode ID persistence, and file-state transitions remain correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestINodeFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLargeDirectoryDelete.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLargeDirectoryDelete.java

**Purpose:** Regression test ensuring recursive deletion of a large directory does not monopolize the NameNode and still allows other client and lock operations to make progress.

**Important APIs and flow:** Static `CONF` uses one-byte HDFS blocks and one-byte checksums so each 100-byte file contributes 100 blocks. `createFiles()` creates files under `/root` with random directory depth until `TOTAL_BLOCKS` reaches 10,000. `getBlockCount()` reads `FSNamesystem.getBlocksTotal()`. `runThreads()` starts two `SubjectInheritingThread` subclasses while deleting `/root`.

**Control flow:** One worker repeatedly creates and deletes small `/tmpN` files while block count is between zero and `TOTAL_BLOCKS`; the other repeatedly acquires and releases the NameNode global write lock and increments `lockOps`. The main thread recursively deletes `/root`, waits for the `BlockManager` marked-delete queue to drain with `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty()`, stops workers, rethrows worker failures, and asserts `lockOps + createOps > 0`.

**State and persistence behavior:** The test mutates a large namespace tree and block map, then verifies deletion processing progresses asynchronously enough for concurrent namespace operations or lock acquisition. It does not restart the cluster; persistence is not the target. The important state is block count, pending deletion queue, and progress counters.

**Dependencies and integration points:** Integrates `MiniDFSCluster`, `DFSTestUtil`, `FSNamesystem` locking with `RwLockMode.GLOBAL`, `BlockManagerTestUtil`, `SubjectInheritingThread`, and recursive `FileSystem.delete()`.

**Risks and test signals:** The random directory shape and concurrent timing can make the exact mix of create and lock operations nondeterministic, so the assertion only requires any progress. Passing signals large recursive deletes yield sufficiently and do not block all NameNode work until every block deletion is processed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLargeDirectoryDelete.java -->
