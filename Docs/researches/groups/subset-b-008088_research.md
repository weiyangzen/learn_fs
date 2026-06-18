# subset-b-008088 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotProvider.java

## Purpose
`TestOzoneManagerSnapshotProvider` verifies that an HA Ozone Manager follower can download a DB checkpoint from the current leader through the OM snapshot provider, and that the downloaded checkpoint carries the same Ratis transaction index as the leader's current snapshot index.

## Important APIs, Types, and Functions
The test builds a 3-OM `MiniOzoneHAClusterImpl`, creates a volume and bucket through `OzoneClientFactory.getRpcClient`, resolves the leader with `OmTestUtil.getCurrentOmProxyNodeId`, and calls `followerOM.getOmSnapshotProvider().downloadDBSnapshotFromLeader(leaderOMNodeId)`. `getDownloadedSnapshotIndex(DBCheckpoint)` opens the checkpoint location as an `InodeMetadataRocksDBCheckpoint`, locates `OzoneConsts.OM_DB_NAME`, and reads `TransactionInfo` through `OzoneManagerRatisUtils.getTrxnInfoFromCheckpoint`.

## Control Flow, State, and Persistence
Setup enables OM HTTP because checkpoint download uses the leader's HTTP endpoint, starts a 3-node HA OM service, and creates initial metadata so the leader has a non-empty DB state. The test selects a follower from the leader peer list, downloads the checkpoint to follower-local storage, extracts the checkpoint transaction index from the RocksDB checkpoint's transaction-info table, and compares it with `leaderOM.getRatisSnapshotIndex()`. State under test is persisted OM RocksDB metadata and Ratis transaction metadata embedded in the checkpoint.

## Dependencies and Integration Points
This test integrates OM HA, OM HTTP snapshot transfer, RocksDB checkpoint layout, OM Ratis transaction metadata, and Ozone client volume/bucket APIs. It depends on mini-cluster leadership discovery and on the checkpoint provider returning a fully materialized checkpoint directory.

## Risks and Test Signals
Main risks are stale leader selection, HTTP-disabled transfer paths, checkpoint directory layout changes, and mismatches between Ratis snapshot index and checkpoint `TransactionInfo`. The signal is strong for leader-to-follower checkpoint correctness, but narrow: it does not validate follower installation of the checkpoint or multi-follower behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotRestore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotRestore.java

## Purpose
`TestOzoneSnapshotRestore` validates restore-like workflows where keys are copied out of Ozone snapshot paths back into live buckets using `OzoneFsShell -cp`. It covers FSO and legacy bucket layouts, cross-bucket restores, cross-layout restores, and restoration after non-contiguous snapshot deletion.

## Important APIs, Types, and Functions
The test enables `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, starts a 3-OM HA cluster, configures OFS via `FS_DEFAULT_NAME_KEY`, and uses `ObjectStore.createSnapshot`, `OmSnapshotManager.getSnapshotPrefix`, `OmSnapshotManager.getSnapshotPath`, and `OzoneFsShell`. Helpers include `createFileKey`, `deleteKeys`, `createSnapshot`, `keyCount`, `keyCopy`, and `waitForKeyCount`. Test cases are parameterized by `BucketLayout.FILE_SYSTEM_OPTIMIZED` and `BucketLayout.LEGACY`, plus mixed source/destination layout pairs.

## Control Flow, State, and Persistence
`init` stops the leader `KeyManagerImpl` deletion services so deleted data remains readable during restore tests. Each test creates volumes, buckets, keys, and a snapshot, waits for the snapshot checkpoint `CURRENT` directory to appear on disk, then uses OFS absolute paths containing the snapshot prefix to copy snapshot keys into a destination bucket. `testUnorderedDeletion` creates ten incremental snapshots, deletes every third snapshot starting at index two, deletes live keys, and restores from the latest snapshot to confirm snapshot chains still expose retained key versions.

## Dependencies and Integration Points
The tests tie together OM snapshot metadata, filesystem snapshot path construction, OFS shell copy semantics, bucket layout translation, key listing, and snapshot checkpoint persistence. They depend on the mini-cluster's client config and on the snapshot directory naming contract used by `OmSnapshotManager`.

## Risks and Test Signals
Risks include asynchronous checkpoint creation, delayed key visibility, deletion services removing data before copy, and known RocksDB seek behavior noted in the cross-bucket test. Test signals are key counts before and after deletion/copy and zero exit codes from the filesystem shell. Coverage focuses on observable restore behavior, not on a first-class restore API.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotRestore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotsNonHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotsNonHA.java

## Purpose
`TestOzoneSnapshotsNonHA` runs the shared `SnapshotTests` suite against a non-HA mini Ozone cluster. Its role is to prove the base snapshot behavior does not depend on OM HA.

## Important APIs, Types, and Functions
The class extends `SnapshotTests` and overrides only `createCluster()`, returning `newClusterBuilder().build()`. It uses JUnit per-class lifecycle through `@TestInstance`.

## Control Flow, State, and Persistence
All test flow lives in the inherited `SnapshotTests`; this subclass only changes cluster topology. Persistent state is whatever the inherited tests create in OM/SCM/DN mini-cluster metadata, but without HA Ratis peer behavior.

## Dependencies and Integration Points
The file integrates the generic snapshot test harness with the default `MiniOzoneCluster` builder. It acts as a topology adapter rather than a standalone test implementation.

## Risks and Test Signals
The main risk is that inherited tests may assume HA-specific timing or APIs despite this non-HA subclass. Signal comes from the base suite executing unchanged on a single-OM topology, catching accidental HA-only assumptions in snapshot logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotsNonHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotBackgroundServices.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotBackgroundServices.java

## Purpose
`TestSnapshotBackgroundServices` exercises HA snapshot background services around follower checkpoint installation, snapshot/key deletion, compaction-log transfer, backup SST pruning, SST filtering, and snapshot diff correctness after leadership transfer.

## Important APIs, Types, and Functions
The test configures HA OM Ratis log purge/segment thresholds and service intervals for block deletion, snapshot deletion, compaction DAG pruning, and SST filtering. Key helpers are `recoverCluster`, `stopFollowerOM`, `startInactiveFollower`, `createSnapshotsEachWithNewKeys`, `getNewLeader`, `confirmSnapDiffForTwoSnapshotsDifferingBySingleKey`, `createOzoneSnapshot`, `getSnapDiffReport`, `getCompactionLogEntries`, `suspendBackupCompactionFilesPruning`, and `resumeBackupCompactionFilesPruning`.

## Control Flow, State, and Persistence
Each test recovers the 3-OM HA cluster, stops one follower, creates OBS-bucket snapshots and keys on the leader, restarts the follower so it installs a checkpoint, performs extra reads/writes, transfers leadership to that follower, and then checks service-specific state on the new leader. The deletion test verifies deleted key propagation between snapshot deleted tables after deleting an intermediate snapshot. The compaction test compares compaction log table entries and forward compaction DAG nodes/edges across old and new leaders. The pruning test suspends RocksDB checkpoint differ pruning, creates snapshots, resumes pruning, and waits for files under the SST backup directory to shrink. The SST filtering test waits for `SstFilteringService.isSstFiltered` on a new snapshot. Snapshot diff assertions validate logical correctness after background processing.

## Dependencies and Integration Points
This file integrates OM HA leadership transfer, Ratis checkpoint catch-up, OM metadata tables, RocksDB checkpoint differ and compaction DAG, SstFilteringService, snapshot deletion services, block deletion intervals, object-store bucket APIs, and asynchronous snapshot diff jobs.

## Risks and Test Signals
Risks are high because the tests rely on timing, leadership transfer, compaction side effects, and background services; one method is explicitly marked flaky. Strong signals include table membership checks, equality of compaction log/DAG state across leaders, SST backup file pruning, filtered snapshot metadata, and exact snapshot diff entries for a single key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotBackgroundServices.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDefragAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDefragAdmin.java

## Purpose
`TestSnapshotDefragAdmin` verifies the `ozone admin om snapshot defrag` command can target OM leader and follower nodes in an HA cluster, with both synchronous and `--no-wait` invocation modes.

## Important APIs, Types, and Functions
Setup enables filesystem snapshots, sets `OZONE_SNAPSHOT_DEFRAG_SERVICE_INTERVAL`, limits per task via `SNAPSHOT_DEFRAG_LIMIT_PER_TASK`, and starts a 3-OM `MiniOzoneHAClusterImpl`. Tests call `executeDefragCommand(nodeId, noWait)`, which constructs an `OzoneAdmin`, imports cluster config, captures stdout, and executes `om snapshot defrag --service-id ... --node-id ...` optionally with `--no-wait`.

## Control Flow, State, and Persistence
The test locates the leader, finds a follower by comparing node IDs, iterates all OMs, and verifies command output. It does not create snapshots or inspect defrag results; it checks command dispatch and response text. The persistent state under test is primarily HA OM service registration and the admin command's ability to route to a target OM node.

## Dependencies and Integration Points
This is an admin CLI integration test covering HA service ID lookup, node ID targeting, snapshot defrag service trigger plumbing, and stdout messaging. It depends on `OzoneAdmin.execute` and cluster-provided configuration resources.

## Risks and Test Signals
The signal is command-level: exit code zero and output containing trigger/completion/background wording. It may miss defrag task correctness, queueing, and actual RocksDB/snapshot state changes. Risks include brittle stdout text assertions and follower routing behavior changing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDefragAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDirectoryCleaningService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDirectoryCleaningService.java

## Purpose
`TestSnapshotDirectoryCleaningService` validates snapshot deep cleaning for FSO directories, including exclusive size accounting and snapshot diff correctness after deleted directories have been deep-cleaned.

## Important APIs, Types, and Functions
The test enables `OZONE_SNAPSHOT_DEEP_CLEANING_ENABLED`, ACLs, low directory/block deleting intervals, and small `OZONE_FS_ITERATE_BATCH_SIZE`. It uses `FileSystem` over an FSO bucket, OM metadata tables (`deletedDirTable`, key table, directory table, deleted key table, snapshot info table), `DirectoryDeletingService`, `SnapshotChainManager`, `SnapshotUtils.getNextSnapshot`, and `ObjectStore.snapshotDiff`.

## Control Flow, State, and Persistence
`testExclusiveSizeWithDirectoryDeepClean` creates nested directory/file trees, snapshots them, adds more files, deletes a subtree and root files, creates more snapshots, waits for directory deletion service runs, and verifies each snapshot's exclusive size plus deep-cleaning delta. Because replication is RATIS/THREE, replicated exclusive size is expected to be three times logical size. `testSnapshotDiffBeforeAndAfterDeepCleaning` suspends deletion services, deletes a directory, snapshots, resumes services, waits for deep cleaning flags on `snap1`, creates a later snapshot, and verifies the diff from `snap2` to `snap3` reports the expected directory creations.

## Dependencies and Integration Points
This file ties FSO namespace operations, OM metadata tables, directory/key deletion background services, snapshot chain traversal, exclusive size accounting, replicated size accounting, and snapshot diff. It depends on asynchronous service progress and direct metadata table row counts.

## Risks and Test Signals
Risks include timing sensitivity, deep-cleaning flags lagging table changes, and brittle expected table row counts. One size test is marked flaky. Test signals include exact table counts, snapshot deep-cleaned flags, exclusive size totals, replicated size totals, and exact snapshot diff entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDirectoryCleaningService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/package-info.java

## Purpose
This `package-info.java` documents the `org.apache.hadoop.ozone.om.snapshot` integration-test package as Ozone Manager tests for the snapshot feature.

## Important APIs, Types, and Functions
The file contains package-level Javadoc only and declares the `org.apache.hadoop.ozone.om.snapshot` package. It exports no runtime APIs, classes, or functions.

## Control Flow, State, and Persistence
There is no executable control flow and no state. Its effect is package documentation for generated Javadocs and source organization.

## Dependencies and Integration Points
The file integrates with Java package documentation tooling. It aligns the snapshot integration-test package with OM snapshot feature ownership.

## Risks and Test Signals
No behavioral test signal exists. Risk is limited to documentation drift if the package broadens beyond snapshot-focused OM tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/package-info.java

## Purpose
This `package-info.java` documents the `org.apache.hadoop.ozone` integration-test package as containing Ozone test utilities.

## Important APIs, Types, and Functions
The file declares package-level Javadoc and the `org.apache.hadoop.ozone` package. It defines no classes, methods, or constants.

## Control Flow, State, and Persistence
There is no executable logic, state mutation, or persistence. Its only role is documentation metadata.

## Dependencies and Integration Points
The file integrates with Java package documentation and gives package-level context for test utility classes under `org.apache.hadoop.ozone`.

## Risks and Test Signals
There are no runtime risks or test signals. Documentation could become stale if the package contents are no longer primarily test utilities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/parser/TestOzoneHARatisLogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/parser/TestOzoneHARatisLogParser.java

## Purpose
`TestOzoneHARatisLogParser` verifies that the debug Ratis log parser can parse both OM HA and SCM HA Ratis segment files produced by a mini HA Ozone cluster.

## Important APIs, Types, and Functions
The test starts a 3-OM, 3-SCM HA cluster, performs volume and bucket requests, stops the cluster, locates Ratis directories via `OzoneManagerRatisUtils.getOMRatisDirectory` and `SCMHAUtils.getSCMRatisDirectory`, and parses segment files with `RatisLogParser.parseRatisLogs`. It uses `OMRatisHelper::smProtoToString` for OM entries and `SCMRatisRequest::smProtoToString` for SCM entries.

## Control Flow, State, and Persistence
Setup creates a small amount of metadata to force Ratis log entries and redirects stdout/stderr to byte buffers. The test stops the cluster before reading local Ratis segment files, asserts expected group/current directory structure, waits for `log_inprogress_0` for OM and `log_inprogress_1` for SCM, parses each file, and checks parser output for `Num Total Entries:`. Persistent state is the on-disk Ratis log directory generated by the HA services.

## Dependencies and Integration Points
This integrates mini HA cluster startup, OM/SCM Ratis storage layout, debug parser CLI internals, and state-machine-proto decoding functions. It depends on exact segment file names and a single Ratis group directory.

## Risks and Test Signals
The test is marked flaky. Risks include segment index/name changes, delayed log creation, extra groups, and parser output text changes. Signal confirms parser can open and decode real OM/SCM logs, but not exact entry contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/parser/TestOzoneHARatisLogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/ReconfigurationTestBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/ReconfigurationTestBase.java

## Purpose
`ReconfigurationTestBase` is a shared abstract base for non-HA integration tests that validate live reconfiguration handlers for Ozone services.

## Important APIs, Types, and Functions
The class implements `NonHATests.TestCase`, captures the current short username via `UserGroupInformation`, requires subclasses to provide `getSubject()`, and exposes `assertProperties(ReconfigurationHandler, Set<String>)`. The assertion checks both `getReconfigurableProperties()` and sorted `listReconfigureProperties()`.

## Control Flow, State, and Persistence
At `@BeforeAll`, the current user is stored for admin-list tests. `assertProperties` verifies that the handler's set of reconfigurable properties and public list output match the expected set. No persistent state is changed by the base class.

## Dependencies and Integration Points
It integrates JUnit per-class lifecycle, the `NonHATests` cluster-injection contract, Hadoop `ReconfigurationHandler`, and current-user lookup. Subclasses for DN, OM, and SCM use it to share property-list validation and current-user expectations.

## Risks and Test Signals
Risk is mostly in expected property-set drift: added or removed reconfigurable keys must be reflected in subclass tests. The base provides a clean signal that handler introspection and list ordering are consistent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/ReconfigurationTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestDatanodeReconfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestDatanodeReconfiguration.java

## Purpose
`TestDatanodeReconfiguration` validates live reconfiguration of datanode properties, especially block deletion and replication thread pool sizing.

## Important APIs, Types, and Functions
The subject is the first `HddsDatanodeService` reconfiguration handler. It expects keys from `DatanodeConfiguration`, `TracingConfig`, `HDDS_DATANODE_BLOCK_DELETE_THREAD_MAX`, block deleting interval/timeout/workers, and `REPLICATION_STREAMS_LIMIT_KEY`. Behavioral tests call `reconfigureProperty` and then inspect `BlockDeletingService`, `DeleteBlocksCommandHandler` executor, and replication server executor.

## Control Flow, State, and Persistence
The tests run against a non-HA cluster provided by `NonHATests`. They mutate live datanode configuration through the reconfiguration handler and immediately verify in-memory service state: block delete limit, delete-block command executor core/max pool sizes, and replication executor core/max pool sizes. No restart or durable config file rewrite is asserted.

## Dependencies and Integration Points
This file connects the generic reconfiguration framework to datanode container services, command dispatch, block deletion, replication server concurrency, tracing config, and datanode config metadata.

## Risks and Test Signals
Risks include thread pool resizing invariants, invalid deltas producing non-positive pools if defaults change, and expected key drift. The signal is direct in-memory observation after reconfiguration, which is stronger than checking only stored config values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestDatanodeReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestOmReconfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestOmReconfiguration.java

## Purpose
`TestOmReconfiguration` validates live OM reconfiguration for admin/read-only admin lists, blacklist settings, list limits, deletion-service controls, and the snapshot SST filtering service interval.

## Important APIs, Types, and Functions
The subject is `cluster().getOzoneManager().getReconfigurationHandler()`. Expected properties combine OM admin keys, deletion interval/thread/limit keys, `OZONE_SNAPSHOT_SST_FILTERING_SERVICE_INTERVAL`, `OmConfig` reconfigurables, tracing config, and blacklist keys. Tests mutate properties through `reconfigureProperty` and inspect `OzoneManager`, `OmConfig`, `KeyManagerImpl`, deleting services, and SST filtering service handles.

## Control Flow, State, and Persistence
Each test updates one property and verifies the live OM object reflects the new value. Admin reconfiguration preserves the current user in the admin set. Blacklist group tests verify replacement rather than accumulation. Boolean parsing for list-all-volumes is tested with normal, empty, and invalid values. The SST filtering test changes the interval to `30s`, confirms the service stays enabled, changes it to `-1`, confirms the service stops and handle becomes null, then restores the original interval and confirms restart.

## Dependencies and Integration Points
This integrates OM reconfiguration, ACL/admin authorization config, key deletion and directory deletion services, `OmConfig`, tracing config, and snapshot SST filtering lifecycle management.

## Risks and Test Signals
Risks include expected key-set drift, service restart leaks, and parsing differences for empty/invalid booleans. The test provides direct signals through OM getters, service enablement flags, and active service references rather than just config strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestOmReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestScmReconfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestScmReconfiguration.java

## Purpose
`TestScmReconfiguration` validates live SCM reconfiguration for admin users, replication-manager settings, block deletion limits, safemode log interval, EC writable container provider settings, SCM config, and tracing config.

## Important APIs, Types, and Functions
The subject is `cluster().getStorageContainerManager().getReconfigurationHandler()`. Expected property sets include `OZONE_ADMINISTRATORS`, `OZONE_READONLY_ADMINISTRATORS`, `HDDS_SCM_SAFEMODE_LOG_INTERVAL`, `ReplicationManagerConfiguration`, `WritableECContainerProviderConfig`, `ScmConfig`, and `TracingConfig`. Behavioral tests inspect SCM admin sets, `ReplicationManagerConfiguration`, `SCMBlockDeletingService`, and SCM configuration values.

## Control Flow, State, and Persistence
Tests call `reconfigureProperty` or `reconfigurePropertyImpl` with new values and assert live SCM state changes immediately. Admin configuration includes current user for full admins and only the configured value for read-only admins. Replication interval and sample limit update the replication manager config object. Block deletion max updates the SCM block deleting service. Safemode log interval is checked in SCM configuration.

## Dependencies and Integration Points
This file integrates the reconfiguration framework with SCM authorization, replication manager, EC container provider config metadata, SCM block deletion, safemode logging, and tracing config.

## Risks and Test Signals
Risks include expected reconfigurable-property drift and differences between handler-level config updates and live service fields. Signals are direct live-object assertions, which catch reconfiguration hooks that update configuration text but not service behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestScmReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/repair/om/TestFSORepairTool.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/repair/om/TestFSORepairTool.java

## Purpose
`TestFSORepairTool` validates the offline OM `fso-tree` repair command against connected, disconnected, empty, non-FSO, filtered, and pending-deletion FSO namespace trees. It verifies dry-run reporting, repair mutations, idempotence, alternate DB directory names, and cluster restart after repair.

## Important APIs, Types, and Functions
The test uses `OzoneRepair().getCmd()` with `om fso-tree --db ...`, `--dry-run`, `--volume`, and `--bucket`. It constructs namespace state through OFS `FileSystem`, `ObjectStore`, and bucket layout APIs, then deliberately corrupts OM RocksDB tables by deleting entries from `directoryTable` or moving entries to `deletedDirTable` using `OMFileRequest.getOmKeyInfo`. Report expectations use `FSORepairTool.Report` and `ReportStatistics`.

## Control Flow, State, and Persistence
`setup` starts a mini cluster, initializes OFS, builds several trees, creates OBS and legacy buckets for skip coverage, captures stdout/stderr, records the OM DB path, and stops the OM before executing the offline tool. Ordered tests first run dry-run/report cases, then run full repair, then run repair again to verify no remaining orphaned objects, and finally restart the OM and count metadata table entries. Helper builders create reachable trees, disconnected orphan trees, empty trees, and trees where a parent is already in the deleted directory table so descendants are classified as unreachable pending deletion rather than orphaned.

## Dependencies and Integration Points
This file integrates the repair CLI, OM RocksDB schema, FSO directory and key tables, deleted directory/deleted key tables, OFS behavior, picocli confirmation input, non-FSO bucket filtering, and mini-cluster restart validation.

## Risks and Test Signals
Risks include direct RocksDB table mutation bypassing normal invariants, test order coupling, stdout formatting brittleness, and offline repair assumptions requiring OM shutdown. Signals include exact report serialization, warning/error text for filters, skip messages for non-FSO buckets, post-repair orphan counts, idempotent second repair, and table counts after OM restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/repair/om/TestFSORepairTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancer.java

## Purpose
`TestDiskBalancer` validates direct client-to-datanode disk balancer RPCs for report retrieval, start/stop-after-even behavior, status reporting, and pause/resume around datanode decommission/recommission.

## Important APIs, Types, and Functions
The test starts a 3-DN mini cluster with `SCMContainerPlacementCapacity`, updates node storage reports with random reports, creates `DiskBalancerProtocolClientSideTranslatorPB` proxies to each DN `CLIENT_RPC` port, and uses `DiskBalancerConfigurationProto`, `DatanodeDiskBalancerInfoProto`, and `DiskBalancerRunningStatus`. It also uses `ContainerOperationClient` to decommission and recommission nodes.

## Control Flow, State, and Persistence
`testDatanodeDiskBalancerReport` queries each DN for disk balancer info and checks volume density and node metadata. `testDiskBalancerStopAfterEven` starts balancing on one DN with `stopAfterDiskEven=true`, observes `RUNNING`, then waits for `STOPPED`. `testDatanodeDiskBalancerStatus` starts balancing on all DNs, verifies `RUNNING`, decommissions one DN, waits for that DN to become `PAUSED`, confirms other in-service DNs remain `RUNNING`, recommissions the DN, and waits for `RUNNING` again. State under test is live DN disk balancer service state and SCM operational state.

## Dependencies and Integration Points
The file connects SCM node manager state, DN client RPC, disk balancer service configuration, placement policy, storage reports, and decommission/recommission workflows.

## Risks and Test Signals
Risks include timing sensitivity in service transitions and random storage report shape. Signals are direct RPC status reads from DNs and SCM node state waits, covering behavior not visible through SCM-only APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerDuringDecommissionAndMaintenance.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerDuringDecommissionAndMaintenance.java

## Purpose
`TestDiskBalancerDuringDecommissionAndMaintenance` validates disk balancer behavior when datanodes enter decommissioning or maintenance states, including automatic pause, explicit stop while paused, and automatic resume only when appropriate.

## Important APIs, Types, and Functions
The test uses a 5-DN mini cluster, `ContainerOperationClient` decommission/maintenance/recommission calls, direct `DiskBalancerProtocol` DN proxies, `DiskBalancerConfigurationProto`, `DiskBalancerRunningStatus`, `NodeManager`, and `DiskBalancerService` log capture. Helpers include `stopDiskBalancer`, `getInServiceDatanodes`, and `queryAllInServiceDatanodes`.

## Control Flow, State, and Persistence
After each test, all DN disk balancers are stopped and verified `STOPPED`. The first test starts balancing on all DNs, decommissions one and starts maintenance on another, queries only in-service DNs to ensure excluded states do not appear, verifies service stop log messages, recommissions the decommissioned DN, and confirms it appears in reports/status and resumes. The second test starts balancing on a DN, decommissions it, verifies `PAUSED`, explicitly stops it, recommissions it, and verifies it stays `STOPPED`. The third decommissions an initially stopped DN, starts disk balancer while decommissioning, verifies it becomes `PAUSED`, then recommissions and verifies it becomes `RUNNING`.

## Dependencies and Integration Points
This integrates SCM node operational state transitions, DN persisted operation state, disk balancer service lifecycle, direct DN RPC status, CLI-equivalent filtering for in-service DNs, and log messages from `DiskBalancerService`.

## Risks and Test Signals
Risks include brittle log text checks, state transition timing, and cross-test contamination if cleanup fails. Signals include direct service status, SCM node-state waits, in-service query filtering, and explicit log evidence for pause/resume decisions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerDuringDecommissionAndMaintenance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerPolicyPerformance.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerPolicyPerformance.java

## Purpose
`TestDiskBalancerPolicyPerformance` stress-tests `DefaultContainerChoosingPolicy` with many volumes and containers, verifies disk-full failure behavior, and checks that deleted or in-progress containers are skipped during candidate selection.

## Important APIs, Types, and Functions
The test builds a mock `MutableVolumeSet` with 20 `HddsVolume` instances using `MockSpaceUsageSource`, creates 100,000 `KeyValueContainer` objects in a `ContainerSet`, wraps them in a mocked `OzoneContainer` and `ContainerController`, and invokes `ContainerChoosingPolicy.chooseVolumesAndContainer`. It uses `DiskBalancerVolumeCalculation.getVolumeUsages`, `ContainerCandidate`, `deltaMap`, `inProgressContainerIDs`, and movable states from `DiskBalancerConfiguration`.

## Control Flow, State, and Persistence
`setup` creates volumes with varied utilization, creates containers biased toward high-utilization volumes, marks some containers in progress, and prepares a fixed thread pool. `testVolumeChoosingFailureDueToDiskFull` raises minimum free space so all volumes are effectively full and expects no candidate. `testConcurrentContainerChoosingPerformance` runs 10 threads for 10,000 iterations each, choosing candidates, adding selected IDs to the in-progress set up to a cap, and adjusting source-volume deltas. `testContainerDeletionAfterIteratorGeneration` chooses one container, marks it in progress, removes a second candidate from memory, then expects the policy to return a different valid container.

## Dependencies and Integration Points
This is mostly an in-process policy test integrating datanode volume abstractions, mock space usage, container metadata, container controller iteration, disk balancer calculations, and concurrency structures.

## Risks and Test Signals
Risks include long runtime, high memory use from 100,000 containers, nondeterminism from random utilization and shuffled IDs, and performance output that is informational rather than asserted. Behavioral signals are null candidate under disk-full constraints, no exceptions/failures during concurrent selection, and explicit skipping of in-progress/deleted containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerPolicyPerformance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestDeletedBlocksTxnShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestDeletedBlocksTxnShell.java

## Purpose
`TestDeletedBlocksTxnShell` verifies the SCM admin subcommand that reports deleted block transaction summary totals.

## Important APIs, Types, and Functions
The test starts a 3-SCM HA mini cluster with one OM, gets the SCM leader, creates synthetic `DeletedBlock` entries, adds them to `DeletedBlockLog`, flushes the leader SCM HA DB transaction buffer, and runs `GetDeletedBlockSummarySubcommand.execute` through a `ContainerOperationClient`. It also seeds `ContainerStateManager` with `ContainerInfo` and three closed `ContainerReplica` entries per container.

## Control Flow, State, and Persistence
`generateData(30)` creates 30 container transaction groups, each containing five deleted blocks of fixed logical and replicated sizes. `updateContainerMetadata` adds closed container metadata and replicas to SCM so the deleted block log can accept transactions. The test flushes SCM leader DB state, asserts summary counts from `DeletedBlockLog.getTransactionSummary`, executes the CLI subcommand, and checks stdout contains the same totals. Persistent state is SCM deleted block log and container metadata in the HA SCM DB.

## Dependencies and Integration Points
This integrates SCM HA, deleted block log, container state manager, container replicas, SCM transaction buffer flushing, admin shell command execution, and stdout capture.

## Risks and Test Signals
Risks include assuming the first leader-ready SCM stream entry is stable and needing manual flush to avoid uncommitted state. Signals are exact totals for transactions, block count, logical size, replicated size, and matching command output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestDeletedBlocksTxnShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneContainerUpgradeShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneContainerUpgradeShell.java

## Purpose
`TestOzoneContainerUpgradeShell` validates the offline repair command `datanode upgrade-container-schema` for upgrading a datanode's container schema after a schema-v2 container has been created and the datanode is moved to schema-v3 configuration.

## Important APIs, Types, and Functions
Setup configures short SCM/DN heartbeat and report intervals, sets replication-manager interval, disables `CONTAINER_SCHEMA_V3_ENABLED`, starts a mini cluster, and creates a client. The test writes a key, closes its container, switches one DN config to schema v3, restarts that DN, writes persisted DN details with `IN_MAINTENANCE`, stops the cluster, and runs `OzoneRepair` with `datanode upgrade-container-schema` and `-D ozone.metadata.dirs=...`.

## Control Flow, State, and Persistence
The flow creates an old-schema container, closes it through SCM, restarts a datanode with schema v3 enabled so its local container data needs upgrade, persists maintenance state to the datanode ID file, shuts down cluster services and caches, then runs the offline upgrade command with confirmation input. Persistent state includes datanode metadata directories, container RocksDB stores, datanode ID file operational state, and container cache/metrics cleanup.

## Dependencies and Integration Points
This integrates client key writes, OM key lookup, SCM container close, datanode restart/config mutation, persisted datanode details, container schema feature flag, repair CLI, metadata directory discovery, container caches, metrics, and RocksDB leak checks.

## Risks and Test Signals
Risks include offline command requiring full cluster shutdown, schema assumptions, cache leakage, and maintenance-state prerequisites. The main signal is exit code zero from the upgrade command after realistic old-schema container creation and shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneContainerUpgradeShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDatanodeShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDatanodeShell.java

## Purpose
`TestOzoneDatanodeShell` validates basic picocli behavior for the `ozone datanode` command: empty invocation should parse and run without error, while an unknown option should fail with a clear message.

## Important APIs, Types, and Functions
The test creates a `TestHddsDatanodeService` subclass overriding `start()` to no-op, obtains `HddsDatanodeService.getCmd()`, and parses through `CommandLine.parseWithHandlers(new RunLast(), exceptionHandler, args)`. Custom `IExceptionHandler2` rethrows parse and execution exceptions so assertions can inspect them.

## Control Flow, State, and Persistence
There is no mini cluster and no persisted state. `testDatanodeCommand` invokes with no args and expects no exception. `testDatanodeInvalidParamCommand` invokes `-invalidParam`, expects an exception, unwraps the cause if present, and checks for `Unknown option: '-invalidParam'`.

## Dependencies and Integration Points
This covers command-line parsing for `HddsDatanodeService` without starting the service. It integrates picocli handlers and datanode command wiring.

## Risks and Test Signals
The signal is limited to parser behavior and error text. Risks are brittle message matching and missing coverage for real subcommands or datanode service startup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDatanodeShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugReplicasVerify.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugReplicasVerify.java

## Purpose
`TestOzoneDebugReplicasVerify` validates `ozone debug replicas verify` checksum behavior against real mini-cluster replicas, including valid input, missing option handling, corrupted block files, and truncated block files.

## Important APIs, Types, and Functions
The abstract test uses `NonHATests.TestCase`, `OzoneDebug`, `TestDataUtil.createKeys`, OM key metadata, `OmKeyLocationInfo`, datanode `ContainerSet`, and helper methods `findFirstBlockFile`, `corruptBlock`, `truncateBlock`, and `getFirstContainer`. It passes OM and SCM addresses through `--set=` arguments.

## Control Flow, State, and Persistence
Before each test, it creates ten keys and records a volume path for debug command input. Cleanup logs captured output and deletes generated keys, buckets, and volumes. The parameterized test verifies `replicas verify` without `--checksums` exits with code 2, and with `--checksums` exits zero and emits no corruption text. Corruption tests locate the first physical `.block` file under a container's `chunks` directory, corrupt or truncate it, execute `replicas verify --checksums --all-results`, and assert the expected diagnostic appears.

## Dependencies and Integration Points
This integrates debug CLI, OM/SCM client configuration, key location metadata, datanode on-disk chunk/block file layout, Xceiver client reads, checksum verification, and physical file mutation utilities.

## Risks and Test Signals
Risks include direct mutation of local replica files, assumptions about `.block` filenames containing local IDs, and cleanup needing to remove all created namespace objects. Signals are exit codes plus explicit output diagnostics: `Checksum mismatch` for corrupted files and `Unexpected read size` for truncated files.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugReplicasVerify.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugShell.java

## Purpose
`TestOzoneDebugShell` validates broader `ozone debug` commands for replica verification, chunk-info output, unique DN block-file paths, and `ldb` scanning of snapshot checkpoint RocksDB databases.

## Important APIs, Types, and Functions
The abstract non-HA test uses `OzoneDebug`, `RDBParser`, `OMMetadataManager`, `TestDataUtil.createVolumeAndBucket/createKey`, RATIS and EC replication configs, `OzoneTestUtils.closeContainer`, OM key lookup through `OmKeyArgs`, and Jackson `ObjectMapper` to parse chunk-info JSON. It parameterizes over EC vs RATIS keys and all `BucketLayout` enum values.

## Control Flow, State, and Persistence
Each test creates a fresh client and debug shell. `testReplicasVerifyCmd` writes a key and runs `replicas verify --checksums --block-existence --container-state`. `testChunkInfoCmdBeforeAfterCloseContainer` runs chunk-info before and after closing the key's container. `testChunkInfoVerifyPathsAreDifferent` parses chunk-info JSON and asserts three distinct block file paths, matching three datanode storage directories. `testLdbCliForOzoneSnapshot` creates a snapshot, constructs the snapshot DB path from the checkpoint directory, waits for `CURRENT`, scans the key table column family via `RDBParser`, and verifies the key name appears.

## Dependencies and Integration Points
This integrates debug CLI commands, OM/SCM address injection, replica verification checks, chunk file path reporting, container close behavior, snapshot checkpoint persistence, RocksDB column-family scanning, and multiple bucket layouts/replication types.

## Risks and Test Signals
Risks include JSON output schema drift, snapshot DB path construction depending on OM storage layout, and asynchronous checkpoint creation. Signals are zero command exit codes, distinct per-DN file paths, and visible snapshot key entries in ldb scan output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRepairShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRepairShell.java

## Purpose
`TestOzoneRepairShell` validates repair-shell commands for updating OM/SCM transaction-info tables offline and triggering OM quota repair/status operations online.

## Important APIs, Types, and Functions
The test uses `OzoneRepair().getCmd()`, `OzoneDebug().getCmd()`, `TransactionInfoRepair.getColumnFamily(Component)`, `RepairTool.Component` values OM and SCM, `OMStorage.getOmDbDir`, `ServerUtils.getScmDbDir`, and confirmation input through `withTextFromSystemIn`. It parses transaction info with regex `([0-9]+#[0-9]+)`.

## Control Flow, State, and Persistence
For each component, the test stops OM and SCM, scans the transaction-info column family with debug `ldb`, records the original highest term/index, runs `om|scm update-transaction --db --term 1111 --index 1111`, verifies stdout and DB scan reflect the update, restores the original term/index, restarts OM, and creates a volume to verify service usability. The quota test checks status, runs dry-run start, confirms status lacks `lastRun`, then runs real quota repair and polls status for completion output.

## Dependencies and Integration Points
This integrates offline repair CLI, debug RocksDB scanner, OM and SCM DB path discovery, transaction-info column families, mini-cluster restart, object-store client operations, and quota repair service endpoints.

## Risks and Test Signals
Risks include regex coupling to ldb output, needing services stopped for DB mutation, stdout text brittleness, and a likely fragile quota completion predicate. Signals include DB scan content before/after repair, successful restoration and OM restart, volume creation after repair, command exit codes, and quota status output changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRepairShell.java -->
