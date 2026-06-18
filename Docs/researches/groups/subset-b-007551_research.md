# Research: subset-b-007551

This grouped report covers the assigned Hadoop HDFS NameNode test files. Each section title preserves the original source path and each section is wrapped with the required reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithAcl.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithAcl.java

Purpose: `TestFSImageWithAcl` verifies that HDFS ACL metadata survives NameNode restarts through both persistence paths: explicit fsimage checkpoint save/load and edit-log replay. It covers ordinary access ACLs, default ACL inheritance into newly created children, root-directory ACL serialization, ACL removal, and post-restart mutability.

Important APIs, types, and functions: the test enables `DFS_NAMENODE_ACLS_ENABLED_KEY` and uses `MiniDFSCluster`, `DistributedFileSystem`, `SafeModeAction`, `AclEntry`, `AclStatus`, and helper builders from `AclTestHelpers`. `testAcl(boolean persistNamespace)` is the shared flow for `testPersistAcl` and `testAclEditLog`; `doTestDefaultAclNewChildren(boolean persistNamespace)` drives the default ACL inheritance tests; `testRootACLAfterLoadingFsImage` checks root ACLs; `restart(DistributedFileSystem, boolean)` optionally enters safe mode, calls `saveNamespace`, leaves safe mode, and restarts the NameNode.

Control flow: setup starts a one-DataNode cluster with ACLs enabled. `testAcl` creates `/p`, adds a named user ACL, restarts either after a checkpoint or without one, reads `getAclStatus` from the namesystem, asserts the named user plus group mask-derived entry, removes the ACL, restarts again, asserts an empty ACL list, then verifies ACL mutation still works after recovery. The default ACL flow creates a parent directory with a default named-user ACL, creates a file and subdirectory, asserts that the file inherited access ACLs and the subdirectory inherited both access and default ACLs plus permission bits, then restarts repeatedly after modifying/removing the parent ACL to prove child ACLs remain stable. The root test adds two named group ACLs to `/`, restarts through fsimage, and reasserts ordered ACL entries.

State and persistence behavior: the core state is namespace ACL metadata stored on `INode`s and reconstructed from either fsimage or edit logs. The tests intentionally exercise saveNamespace by entering safe mode before checkpointing and also exercise replay by restarting without a checkpoint. They also validate that inherited child ACL state is materialized at child creation and not dynamically tied to later parent ACL changes.

Dependencies and integration points: depends on NameNode ACL configuration, `FSNamesystem.getAclStatus`, ACL edit logging, fsimage ACL sections, safe mode namespace save, and `MiniDFSCluster` restart. It integrates with `FSAclBaseTest` helpers only through static ACL entry construction and permission assertions.

Risks and edge cases: ordering of returned ACL entries is asserted exactly, so serializer/deserializer or comparator changes can break the test. The class-level cluster is shared across test methods, so paths like `/p`, `/dir`, and `/` ACL state may leak if a prior test fails before cleanup. Default ACL inheritance with permission bit expectations is sensitive to ACL mask calculations. The root ACL case covers a special inode that often bypasses ordinary parent/child paths.

Test signals: strong signals are exact `assertArrayEquals` checks before and after restarts, `assertPermission` for inherited subdirectory mode `010775`, and paired fsimage/edit-log variants for both simple and default ACL flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshot.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshot.java

Purpose: `TestFSImageWithSnapshot` is a broad regression suite for fsimage save/load behavior when snapshots, snapshot diffs, renames, deleted references, append-under-construction files, and snapshottable directory metadata are present. It checks both direct `FSImageFormat` load from a temporary image and full cluster restart with `format(false)`.

Important APIs, types, and functions: the class uses `MiniDFSCluster`, `FSNamesystem`, `DistributedFileSystem`, `SnapshotTestHelper`, `FSImageFormatProtobuf.Saver`, `FSImageCompression`, `FSImageFormat.LoaderDelegator`, `SaveNamespaceContext`, `Canceler`, `RwLockMode`, `NamespacePrintVisitor`, `DiffList<DirectoryDiff>`, and `SnapshottableDirectoryStatus`. Key helpers are `saveFSImageToTempFile`, `loadFSImageFromTempFile`, `dumpTree2File`, `checkImage`, `appendFileWithoutClosing`, `restartCluster`, and tree-printing/rename helpers.

Control flow: each test starts a fresh one-DataNode cluster. `testSnapshotOnRoot` allows a snapshot on `/`, restarts, saves namespace, restarts again, and checks root diff list and SnapshotManager snapshottable directory listing. `testSaveLoadImage` builds a layered namespace with snapshots, permission changes, creates, deletes, owner changes, and renames, calling `checkImage` after major mutation phases. `checkImage` dumps the namespace tree, saves a protobuf fsimage under the namesystem read lock, records snapshot counters/listings, shuts down/reformats the cluster, loads the image under namesystem and FSDirectory write locks, updates quota counts, dumps the tree again, and compares the before/after dumps.

State and persistence behavior: the file is centered on persistence of snapshot diff chains, inode reference graphs, file metadata, snapshottable directory registries, and under-construction file state. It differentiates live namespace state, checkpointed fsimage state, edit-log replay state, and manually loaded image state. The append tests save/load while the last block length has been updated with `hsync(UPDATE_LENGTH)` but streams are still open.

Dependencies and integration points: depends on snapshot internals (`Snapshot`, `DirectoryDiff`, `DiffList`), namespace tree dump/print visitors, NameNode safe mode checkpointing, protobuf fsimage saver/loader, quota recomputation, HDFS client append/create/rename/delete APIs, and `DFSTestUtil` file creation. It also exercises NameNode storage naming via `NNStorage.NameNodeFile.IMAGE`.

Risks and edge cases: direct image loading after cluster reformat is a high-value signal but can miss restart-side initialization behavior unless covered by separate restart tests. Many tests rely on tree dump textual equality, which is sensitive to dump formatting and ordering. The snapshot deletion and rename tests encode subtle reference-count and diff-merge cases where stale created-after-snapshot children must be destroyed, not serialized. Several tests perform saveNamespace and restart without detailed post-restart assertions beyond absence of failure, which catches load exceptions but not every semantic drift.

Test signals: strong signals include before/after namespace dump equality, snapshot count and snapshottable directory listing equality, root diff validation, file length after edit-log append replay, direct existence checks in snapshot paths, and repeated restart-after-delete/rename sequences. Timeouts on append and rename tests detect hangs in image loading or snapshot diff recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshotParallelAndCompress.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshotParallelAndCompress.java

Purpose: this subclass is intended to rerun `TestFSImageWithSnapshot` under fsimage compression and parallel image loading settings, so the inherited snapshot persistence tests also cover compressed/parallel loader code paths.

Important APIs, types, and functions: it extends `TestFSImageWithSnapshot`, overrides `createCluster`, configures `DFS_IMAGE_COMPRESS_KEY`, `DFS_IMAGE_COMPRESSION_CODEC_KEY` with `GzipCodec`, `DFS_IMAGE_PARALLEL_LOAD_KEY`, `DFS_IMAGE_PARALLEL_INODE_THRESHOLD_KEY`, `DFS_IMAGE_PARALLEL_TARGET_SECTIONS_KEY`, and `DFS_IMAGE_PARALLEL_THREADS_KEY`, then builds `MiniDFSCluster` and refreshes inherited `fsn` and `hdfs`. It also disables snapshot logs and sets `INode.LOG` to TRACE.

Control flow: inherited `setUp` initializes `conf = new Configuration()` and calls this override. The override first sets compression and parallel-load properties, then assigns `conf = new Configuration()` and constructs the cluster. Because the reset occurs after setting the properties, the actual cluster configuration appears to lose the intended compression and parallel-load settings.

State and persistence behavior: intended state is the same snapshot fsimage state covered by the parent class, but persisted through compressed fsimage and loaded through parallel image-load sections. As written, the local reassignment of `conf` likely means parent behavior is executed with default image settings, so the targeted compressed/parallel state may not be persisted.

Dependencies and integration points: integrates only by inheritance with every test in `TestFSImageWithSnapshot`. It depends on the compression codec configuration and parallel fsimage loader thresholds/threads, plus the parent class's direct fsimage save/load helpers.

Risks and edge cases: the configuration-reset ordering is a likely test bug or coverage hole: it undermines the class name and comment claiming both parallelization and compression are enabled. If fixed, inherited tests may expose new timing/ordering behavior in the parallel loader. Because it inherits many expensive tests, failures can be expensive to triage unless the configuration actually differs from the parent.

Test signals: if configuration ordering is corrected, the inherited parent assertions become signals for compressed and parallel load correctness. In the current source, the most important signal for reviewers is the mismatch between intended configuration and actual cluster construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithSnapshotParallelAndCompress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java

Purpose: `TestFSImageWithXAttr` verifies that extended attributes survive NameNode restart through both edit-log replay and fsimage checkpoint persistence, including create, replace, null-value storage, empty byte-array retrieval, and removal.

Important APIs, types, and functions: the test enables `DFS_NAMENODE_XATTRS_ENABLED_KEY`, uses `MiniDFSCluster`, `DistributedFileSystem`, `XAttrSetFlag.CREATE/REPLACE`, `SafeModeAction`, and `Map<String, byte[]>` returned by `getXAttrs`. The shared `testXAttr(boolean persistNamespace)` is invoked by `testPersistXAttr` and `testXAttrEditLog`; `restart` optionally checkpoints through safe mode.

Control flow: setup creates a one-DataNode cluster with XAttrs enabled. The test creates `/p`, sets three XAttrs (`user.a1`, `user.a2`, and `user.a3` with null value), restarts by the selected persistence lane, asserts all three names and byte values, replaces `user.a1`, restarts again, asserts the replacement while preserving others, removes all XAttrs, restarts again, and expects an empty result map.

State and persistence behavior: it exercises inode XAttr storage, edit-log operations for set/replace/remove, fsimage serialization of XAttrFeature, and conversion of null values to the empty byte-array form returned by `getXAttrs`.

Dependencies and integration points: depends on NameNode XAttr configuration, HDFS client XAttr APIs, safe mode checkpointing, cluster restart, and byte-array equality assertions.

Risks and edge cases: exact map size checks catch duplicates and missed removals, while `assertArrayEquals` catches value corruption. The class-level shared cluster can retain `/p` state between methods if a prior method fails. The null-vs-empty value behavior is subtle and should remain intentionally documented because `name3` is set with `null` but asserted as `{}`.

Test signals: paired fsimage/edit-log tests, byte-level assertions for all values, replace-after-restart, and remove-after-restart are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java

Purpose: `TestFSNamesystem` covers focused FSNamesystem unit behaviors: duplicate edit-dir normalization, lease cleanup during `clear`, safemode state distinctions, replication queue activation, HA state exposure in namespace info, reset/image-loaded state, layout-version selection, safemode replication configuration, and audit logger initialization.

Important APIs, types, and functions: it uses `FSNamesystem.getNamespaceEditsDirs`, `FSNamesystem.loadFromDisk`, `FSNamesystem.clear`, `FSNamesystem.getEffectiveLayoutVersion`, `BlockManager`, `LeaseManager`, `NamespaceInfo`, `NameNode.initMetrics`, mocked `FSImage`/`FSEditLog`/`NNStorage`, `Whitebox`, and `TopAuditLogger`. The helper `clearNamesystem` wraps `fsn.clear()` in the global write lock and asserts `isImageLoaded` flips false. `DummyAuditLogger` implements `AuditLogger` for config-driven instantiation tests.

Control flow: tests either construct a lightweight FSNamesystem around mocked storage/edit log or build/format a small real namespace. Safemode tests manually call `enterSafeMode` and `leaveSafeMode` and assert startup-vs-low-resource semantics. Replication queue activation spies the FSNamesystem and mocks HA context/state so `shouldPopulateReplQueues` returns true, then observes `BlockManager.isPopulatingReplQueues` across first and later safemode transitions. Audit logger tests mutate the same `Configuration` through several combinations of default, top, and custom logger strings and assert resulting logger types.

State and persistence behavior: the file tests in-memory namesystem state rather than full persistence, except `testFSNamespaceClearLeases`, which formats a NameNode directory and loads the namesystem from disk before adding a synthetic lease. It verifies reset clears namespace children, leases, and image-loaded state, then allows image-load completion again.

Dependencies and integration points: depends on metrics initialization, HA service state, block management, audit logger plugin loading, caller-context configuration, and filesystem cleanup under `MiniDFSCluster.getBaseDirectory`.

Risks and edge cases: use of `Whitebox` and Mockito against internal fields makes tests sensitive to refactors. `testInitAuditLoggers` reuses mutable `Configuration`, so prior settings can affect later cases unless deliberately overwritten. Some assertions use boolean expressions inside `assertTrue` instead of more precise assertions, making failure messages less diagnostic.

Test signals: exact edit-dir count, lease count before/after clear, safemode boolean transitions, replication queue activation state, non-null HA state in `NamespaceInfo`, effective layout-version matrix, private safe-replication value, and audit logger list size/type composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java

Purpose: `TestFSNamesystemLock` validates the NameNode namesystem read/write lock wrapper: fairness configuration, reentrant compatibility counters, queued waiter counts, long-held lock logging and suppression, stack-trace attribution for read locks, and detailed hold-time metrics.

Important APIs, types, and functions: it targets `FSNamesystemLock`, `DFS_NAMENODE_FSLOCK_FAIR_KEY`, read/write reporting threshold keys, `DFS_LOCK_SUPPRESS_WARNING_INTERVAL_KEY`, `DFS_NAMENODE_LOCK_DETAILED_METRICS_KEY`, `FakeTimer`, `GenericTestUtils.LogCapturer`, `SubjectInheritingThread`, `MetricsRegistry`, `MutableRatesWithAggregation`, and metrics assertions `assertGauge`/`assertCounter`.

Control flow: fairness and compatibility tests directly acquire/release locks and inspect hold counts. Waiter-count testing holds the write lock, starts three reader tasks, and waits until `getQueueLength` equals the blocked thread count. Long-write and long-read tests advance a `FakeTimer` across configured thresholds, clear captured logs, unlock, and assert whether the method name, start date, interval text, and suppression count appear. Read-lock tests also run separate threads to ensure the longest held read lock's stack trace is reported and a shorter concurrent reader is not blamed. Metrics tests unlock with operation names and validate per-operation plus overall nanosecond averages and operation counts.

State and persistence behavior: no persistence; all state is lock-local counters, reentrant hold tracking, suppression timestamps, log buffers, and metrics accumulators. `FakeTimer` makes threshold behavior deterministic without real sleeps.

Dependencies and integration points: integrates with FSNamesystem logging, Hadoop metrics2 rates aggregation, DFS lock configuration keys, thread scheduling, and the lock's operation-name API (`readUnlock("foo")`, `writeUnlock("baz", false)`, suppression variant).

Risks and edge cases: logging assertions depend on message structure and stack trace depth. Concurrent tests can be sensitive to thread scheduling, though latches and `FakeTimer` reduce timing risk. The waiter test starts threads that block on a held write lock and does not explicitly release/stop them in the visible flow, relying on process/test lifecycle behavior after assertion.

Test signals: fairness flag on the underlying lock, read/write hold counts, queued reader count, presence/absence of log text under threshold/suppression conditions, correct longest-reader stack trace, suppression counters, and detailed metrics names/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java

Purpose: this integration test ensures long namesystem lock reports include meaningful operation context: user, authentication method, client IP, source, destination, and permission status for common filesystem operations.

Important APIs, types, and functions: setup uses `MiniDFSCluster`, `HdfsConfiguration`, `DFSTestUtil.getFileSystemAs`, `UserGroupInformation`, `GenericTestUtils.LogCapturer`, and lock threshold keys set to zero. Two functional interfaces (`SupplierWithException`, `Procedure`) allow a single `testLockReport` helper to wrap operations that return a value or not. `matches` scans captured log lines with regular expressions.

Control flow: setup makes every read/write lock report visible by zeroing thresholds and suppression interval, starts a four-DataNode cluster, creates a test user `bob` in supergroup `hadoop`, and captures `FSNamesystem.LOG`. The main test obtains a filesystem as `bob`, runs create/open/setPermission/setOwner/listStatus/getFileStatus/mkdirs/rename/delete under `userGroupInfo.doAs`, and after each operation asserts one log line matches the expected context regex. Streams returned by create/open are closed by the caller after the assertion.

State and persistence behavior: the persistent state is the HDFS namespace objects created and mutated during the operation sequence (`/file`, `/dir`, rename to `/file2`, delete). The test's target state is transient log output from lock reporting, not fsimage/edit-log persistence.

Dependencies and integration points: depends on RPC/user context propagation into namesystem operations, permission/status formatting, `FSNamesystemLock` long-hold report context capture, log text emitted by `FSNamesystem`, and HDFS client APIs.

Risks and edge cases: regexes are intentionally flexible for IP addresses but strict for operation names and permission strings. Comments for rename/delete are swapped in one area, but assertions use the correct regexes. Setting thresholds to zero makes any implementation change in report emission volume visible. The test can be brittle if permission string formatting changes.

Test signals: captured lock report lines must match per-operation context after each HDFS call. The sequence also verifies context changes after `setPermission` and `setOwner` are reflected in later rename logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java

Purpose: `TestFSNamesystemMBean` validates NameNode/FSNamesystem JMX exposure, ensuring attributes are present, have expected types/values, and can be served even when the namesystem write lock or FSEditLog monitor is held by another thread. It also verifies edit-log sync metrics and reconstruction queue initialization progress.

Important APIs, types, and functions: it uses the platform `MBeanServer`, object names `Hadoop:service=NameNode,name=FSNamesystem`, `FSNamesystemState`, and `NameNodeInfo`, `NameNodeMXBean`, Jetty `JSON.parse`, `ConfigBuilder`/`TestMetricsConfig`, `SubjectInheritingThread`, `MiniDFSCluster`, `DFSTestUtil`, and `GenericTestUtils.waitFor`. `MBeanClient` iterates all attributes for the three MBeans and marks success if every `getAttribute` returns without exception.

Control flow: the basic test starts a cluster, reads `SnapshotStats`, parses it as JSON, and compares snapshot counters with `FSNamesystem`. It also asserts `PendingDeletionBlocks` is a `Long` and `NumEncryptionZones` is an `Integer`. Lock tests configure a short metrics cache period, start a cluster, hold either the FSNamesystem global write lock or synchronize on the edit log, wait for cache expiry, run `MBeanClient`, and assert JMX calls complete within 20 seconds. Metrics tests create directories to force edit-log syncs and read `TotalSyncCount`/`TotalSyncTimes`. Reconstruction progress creates a file, restarts the NameNode, waits until progress becomes `1.0`, and checks both direct API and MBean attribute.

State and persistence behavior: tests observe runtime MBean state derived from namespace counters, edit-log sync stats, and block reconstruction initialization. The reconstruction test crosses a NameNode restart, so it also checks post-restart metric progression after processing mis-replicated blocks.

Dependencies and integration points: depends on Hadoop metrics2 JMX registration, FSNamesystem direct MBean registration, NameNode edit-log metrics, reconstruction queue initialization, metrics cache configuration files, and lock-free/cache-safe JMX access patterns.

Risks and edge cases: swallowing exceptions in `MBeanClient` hides root cause, only exposing `succeeded=false`. JMX object names and attribute names are string contracts and brittle under metric renames. The lock tests rely on cache period and join timeout to detect deadlock risk. Writing the metrics config file can affect other metrics tests if not isolated by test filename handling.

Test signals: parsed `SnapshotStats` counters match namesystem APIs, type assertions for MBean attributes, successful full attribute sweep while locks are held, positive sync count with non-null sync times, and reconstruction progress reaching `1.0` after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java

Purpose: `TestFSPermissionChecker` is a direct unit suite for ACL-based permission resolution in `FSPermissionChecker`. It cross-validates HDFS ACL behavior against expected POSIX ACL semantics for owners, named users, groups, named groups, masks, traversal denial, default-only ACL entries, and other permissions. It also tests slow access-control-enforcer reporting.

Important APIs, types, and functions: it builds an in-memory `FSDirectory` with a mocked `FSNamesystem`, creates `INodeDirectory` and `INodeFile` objects, updates ACLs via `AclStorage.updateINodeAcl`, resolves paths through `FSDirectory.getINodesInPath`, and invokes `getPermissionChecker(...).checkPermission`. Helper methods are `addAcl`, `assertPermissionGranted`, `assertPermissionDenied`, `createINodeDirectory`, `createINodeFile`, and the slowness check around `FSPermissionChecker.runCheckPermission`.

Control flow: setup mocks `createFsOwnerPermissions` to return immutable permission status for superuser/supergroup, then creates an `FSDirectory`. Each ACL test constructs a small inode tree, attaches ACL entries, then checks grants/denials for synthetic users `bruce`, `diana`, and `clark`. Denial assertions require `AccessControlException` and verify the error message includes the user name and parent path. The final slowness test creates a threshold-aware message function, runs a fast lambda and a sleeping lambda through `runCheckPermission`, and expects null vs non-null messages.

State and persistence behavior: no on-disk persistence; state is in-memory inode metadata, ACL features, current snapshot ID, and user/group identity. It tests permission semantics independently from RPC, edit logs, or cluster setup.

Dependencies and integration points: depends on ACL helper construction, `FSDirectory.DirOp.READ`, inode child attachment, snapshot current-state constants, `INodeAttributeProvider.AccessControlEnforcer` class metadata for slow-check messages, and UGI group membership.

Risks and edge cases: direct inode construction uses `GRANDFATHER_INODE_ID` repeatedly, which is acceptable for permission resolution but not representative of full namespace invariants. Tests are sensitive to exact ACL mask semantics and parent-path text in denial messages. Default ACL entries in traversal tests must not incorrectly influence access ACL resolution.

Test signals: every permission matrix uses explicit grant/deny assertions for compound actions (`READ_WRITE`, `READ_EXECUTE`, `WRITE_EXECUTE`, `ALL`), denial messages must identify the user and parent, and slow enforcer logic must distinguish fast and delayed runners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java

Purpose: `TestFavoredNodesEndToEnd` verifies that client-specified favored DataNodes influence block placement for create, append, and builder-based create APIs, and that HDFS gracefully falls back when favored nodes are absent or unsuitable.

Important APIs, types, and functions: it uses a 10-DataNode `MiniDFSCluster`, `DistributedFileSystem.create` overloads with `InetSocketAddress[]` favored nodes, `append(..., favoredNodes)`, `createFile(...).favoredNodes(...).build()`, `BlockPlacementPolicy`, `DatanodeInfo.setDecommissioned`, `getBlockLocations`, `DFSTestUtil.waitReplication`, and helper methods `getDatanodes`, `getStringForInetSocketAddrs`, `compareNodes`, and `getArbitraryLocalHostAddr`.

Control flow: class setup starts the cluster once and caches DataNodes. The main create test loops over ten files, picks three unique random DataNodes, creates a file with replication 3 and favored nodes, writes bytes, then asserts all block location names are among the favored nodes. The absent-node test passes three arbitrary localhost ports not belonging to the cluster and only asserts write/replication succeeds. The not-good-node test decommissions one favored node, creates a file with four candidate addresses, restores the node, and asserts replicas exclude the decommissioned address while remaining within the favored list. Append and builder tests mirror the create test through their respective APIs.

State and persistence behavior: state is live block placement and DataNode membership, not fsimage persistence. The decommission test temporarily mutates `DatanodeInfo` state and restores it with `stopDecommission`.

Dependencies and integration points: exercises NameNode block placement, client favored-node hint propagation, DataNode xfer addresses, block location reporting, replication wait logic, and create/append builder API integration.

Risks and edge cases: random selection uses current time, so it is non-deterministic but constrained to unique choices. Tests assume one block per file and exactly three hosts, which follows tiny writes and replication 3. The absent-node test has weak assertions beyond no failure and block-location shape. Address string comparison uses `ip:port` from `BlockLocation.getNames`, so formatting changes could break assertions.

Test signals: block locations must be a subset of selected favored nodes for create/append/builder paths, absent nodes must not fail writes, and a decommissioned favored node must be excluded from actual targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java

Purpose: `TestFileContextAcl` reruns the shared HDFS ACL base test suite through the `FileContext` API surface rather than the ordinary `DistributedFileSystem` ACL methods, proving both client APIs reach equivalent NameNode ACL behavior.

Important APIs, types, and functions: it extends `FSAclBaseTest`, initializes `conf` and `startCluster` in `@BeforeAll`, overrides `createFileSystem`, and defines `FileContextFS extends DistributedFileSystem`. `FileContextFS.initialize` calls `super.initialize` and creates a `FileContext`, while ACL methods (`modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`) delegate to `FileContext`.

Control flow: the inherited base tests call `createFileSystem`; this class returns a `DistributedFileSystem` facade whose ACL operations are routed through `FileContext`. Non-ACL filesystem operations still use the superclass `DistributedFileSystem` behavior, limiting this adapter to the API boundary under test.

State and persistence behavior: persistence and namespace state are controlled by the inherited base tests and shared mini cluster. This class adds no storage behavior; it verifies that FileContext-driven ACL mutations/readbacks affect the same HDFS namespace state.

Dependencies and integration points: depends on `FSAclBaseTest` for coverage, cluster lifecycle, and assertions; `FileContext.getFileContext(conf)` for the alternate API; and HDFS ACL NameNode operations.

Risks and edge cases: because only ACL methods are overridden, any inherited test that performs a non-ACL operation still goes through `DistributedFileSystem`, which is intended but means this is not a full FileContext filesystem facade. Coverage is tied entirely to the base class; changes there can expand or break this adapter.

Test signals: all inherited ACL tests must pass while ACL calls are delegated through `FileContext`, indicating API parity for ACL operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java

Purpose: `TestFileContextXAttr` reruns the shared XAttr base suite through `FileContext` XAttr APIs, checking parity with the normal HDFS client API for set, get, list, and remove extended attributes.

Important APIs, types, and functions: it extends `FSXAttrBaseTest`, overrides `createFileSystem`, and defines `FileContextFS extends DistributedFileSystem`. Overridden methods delegate `setXAttr` with and without flags, `getXAttr`, `getXAttrs`, `getXAttrs(names)`, and `removeXAttr` to a `FileContext` created at initialization.

Control flow: inherited XAttr tests receive the adapter filesystem. General filesystem setup and non-XAttr calls use `DistributedFileSystem`; XAttr-specific calls are routed to `FileContext`, exercising that API path against the same mini cluster and namespace.

State and persistence behavior: state is HDFS inode XAttr metadata manipulated by inherited tests. This class contributes no direct persistence checks beyond whatever `FSXAttrBaseTest` performs; it focuses on API equivalence.

Dependencies and integration points: depends on `FSXAttrBaseTest`, `FileContext`, `XAttrSetFlag`, `DistributedFileSystem`, and the NameNode XAttr implementation.

Risks and edge cases: like the ACL adapter, it is only a partial facade. Any un-overridden XAttr overload would bypass the FileContext path if added to the base suite. The class assumes base static configuration/cluster setup is already supplied by `FSXAttrBaseTest`.

Test signals: inherited XAttr tests pass while XAttr operations delegate through `FileContext`, confirming FileContext behavior for the covered overloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileJournalManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileJournalManager.java

Purpose: `TestFileJournalManager` validates local edit-log segment discovery, reading, recovery, corruption handling, gap behavior, remote edit-log listing, finalization error propagation, and pre-upgrade rename failure handling for `FileJournalManager`.

Important APIs, types, and functions: it uses `FileJournalManager`, `NNStorage`, `StorageDirectory`, `NameNodeDirType.EDITS`, `EditLogInputStream`, `FSEditLogOp`, `JournalSet.EDIT_LOG_INPUT_STREAM_COMPARATOR`, `TestEditLog.setupEdits`, `AbortSpec`, `TXNS_PER_ROLL`, `TXNS_PER_FAIL`, `NNStorage` file-name helpers, `FileUtil`, `NativeCodeLoader`, and `IOUtils.cleanupWithLogger`. Core helpers are `getNumberOfTransactions`, `getJournalInputStream`, `corruptAfterStartSegment`, and `getLogsAsString`.

Control flow: setup disables fsync for speed and creates a fresh `Configuration`. Transaction counting selects input streams from a transaction ID, optionally includes in-progress streams, skips to the current txid, reads operations, and optionally stops on gaps. Tests generate edit directories with different roll/failure patterns, instantiate a manager per storage directory, and assert readable transaction counts. Gap tests delete a finalized edits file and check counts before/at/after the gap. Corruption tests modify an in-progress file after the start segment and expect the manager to recover usable transactions. Remote-log tests mock storage directory contents and assert stringified finalized ranges. Upgrade/finalize tests force filesystem permission errors and assert exceptions plus storage-directory removal or native rename message content.

State and persistence behavior: this file is all about persistent edit-log files under storage directories. It exercises finalized `edits_start-end`, `edits_inprogress_start`, corrupt in-progress segments, deleted segment gaps, storage-dir removal state in `NNStorage`, and pre-upgrade directory renames.

Dependencies and integration points: depends heavily on `TestEditLog` fixtures, local filesystem permissions, native IO availability, edit-log stream ordering, NNStorage naming conventions, and the journal manager's contract with remote edit-log listing and upgrade hooks.

Risks and edge cases: filesystem permission manipulation can behave differently on platforms or when tests run with elevated privileges. `corruptAfterStartSegment` uses a fixed offset and raw overwrite, which is coupled to edit-log binary layout enough to be useful but potentially brittle. Gap behavior is intentionally non-throwing in `getNumberOfTransactions` when `abortOnGap` is true; callers must interpret counts carefully. Static skip-fsync setting affects all edit-log output streams in the JVM.

Test signals: exact transaction counts for normal, mixed, and failed directories; zero count at a gap; corruption recovery count; exclusion of in-progress streams; correct first op when starting mid-segment; remote finalized range lists; expected exceptions on invalid dirs, finalization errors, and pre-upgrade rename failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileJournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java

Purpose: `TestFileLimit` verifies NameNode filesystem object limits, maximum blocks per file, and minimum block size enforcement in real mini clusters, including a simulated storage variant for the object-limit test.

Important APIs, types, and functions: it uses `DFS_NAMENODE_MAX_OBJECTS_KEY`, `DFS_BLOCKREPORT_INTERVAL_MSEC_KEY`, `DFS_HEARTBEAT_INTERVAL_KEY`, `DFS_NAMENODE_MAX_BLOCKS_PER_FILE_KEY`, `DFS_NAMENODE_MIN_BLOCK_SIZE_KEY`, `MiniDFSCluster`, `FSNamesystem.getBlocksTotal`, `FSDirectory.totalInodes`, `DFSTestUtil.createFile`, `SimulatedFSDataset.setFactory`, and `HdfsDataOutputStream.hflush`. `waitForLimit` polls until block plus inode counts reach the expected total.

Control flow: `testFileLimit` configures a low object limit, creates enough files to consume root inode plus file/block objects, asserts another file creation fails, deletes a file and waits for counts to drop, recreates it, deletes again, creates two directories in its place, and asserts a further mkdir fails. `testFileLimitSimulated` toggles `simulatedStorage` and reruns the same flow. `testMaxBlocksPerFileLimit` writes exactly the configured block count, flushes, then writes one more byte and expects an IOException containing the max-blocks message. `testMinBlockSizeLimit` creates with the minimum allowed block size, then expects failure for one byte below minimum.

State and persistence behavior: state is live NameNode inode/block accounting and cluster block reports/heartbeats. The tests do not restart the cluster; they wait for asynchronous block count changes after deletion.

Dependencies and integration points: depends on mini cluster block reporting, FSNamesystem quota/object accounting, DataNode simulated dataset factory, HDFS create/write/flush APIs, and exception message text.

Risks and edge cases: `waitForLimit` is an unbounded polling loop with `Thread.sleep`, so a count regression can hang until the test framework kills it. `simulatedStorage` is an instance field toggled around a direct method call; a failure before reset can affect later state in the same instance. The file-limit test catches broad `IOException` and only checks that an exception happened, not the specific limit type.

Test signals: successful creation up to limit, failure past limit, count drop after delete, success after freeing capacity, max-blocks exception after extra write/flush, and minimum-block-size exception text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileLimit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileTruncate.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileTruncate.java

Purpose: `TestFileTruncate` is the main HDFS truncate regression suite. It covers byte-level truncate semantics, idempotence, quota and content summary accounting, snapshots and copy-on-truncate, lease/block recovery, concurrent truncate rejection, DataNode restarts/shutdowns, edit-log replay, upgrade/rollback, shell command behavior, symlinks, rolling upgrade cleanup, concat on inode references, and rename/snapshot interactions.

Important APIs, types, and functions: it uses `DistributedFileSystem.truncate`, `CommonPathCapabilities.FS_TRUNCATE`, `MiniDFSCluster`, `DFSTestUtil`, `AppendTestUtil`, `LocatedBlocks`, `Block`, `BlockManagerTestUtil`, `NameNodeAdapter`, `FSDirTruncateOp.prepareFileForTruncate`, `FSNamesystem`, `INodesInPath`, `INodeFile`, `FSEditLog.logTruncate`, `DataNodeFaultInjector`, `FsDatasetTestUtils`, `DFSAdmin`, `FsShell`, `ToolRunner`, `StartupOption.UPGRADE/ROLLBACK/REGULAR`, and helper methods `writeContents`, `checkBlockRecovery`, `getLocatedBlocks`, `assertBlockExists`, `assertBlockNotPresent`, `assertFileLength`, `checkFullFile`, `restartCluster`, and `truncateAndRestartDN`.

Control flow: setup creates a three-DataNode cluster with tiny block size/checksum size, short heartbeat, and short reconstruction pending timeout. Basic tests create files of varying lengths, truncate to every smaller length, assert the return value is ready only for no-op or block-boundary truncates, wait for recovery when needed, verify quota space and file content, and repeat random multiple truncates idempotently. Snapshot tests create snapshots before append/truncate sequences, delete snapshots in all orders, and verify snapshot file lengths, live file length, block presence, inode-map size, and content summary after each deletion. Failure tests reject truncate on open/append files, negative/larger sizes, directories, missing files, and permission-denied users, then simulate all DataNodes down and observe lease recovery before completing.

State and persistence behavior: the suite targets live inode length, under-construction state, block IDs, generation stamps, block recovery IDs, copy-on-truncate block replacement, snapshot-retained blocks, namespace quota usage, edit-log truncate replay, and upgrade rollback state. `testTruncateEditLogLoad` saves a clean namespace, truncates, restarts the NameNode, manually recovers the lease, and verifies content. `testUpgradeAndRestart` truncates before and during upgrade, verifies copy-on-truncate while upgrading, rolls back to the pre-upgrade length, restarts regularly, checkpoints, and revalidates block counts and snapshot content.

Dependencies and integration points: integrates with the NameNode truncate path (`FSDirTruncateOp`), lease manager, block manager, DataNode block recovery, snapshots, quota/content summary, shell and admin tools, symlink resolution, rolling upgrade machinery, edit logs, and cluster restart/upgrade paths.

Risks and edge cases: the test is timing-heavy; `checkBlockRecovery` polls up to configured attempts and several tests sleep or restart DataNodes. Tiny block size makes edge cases dense but can differ from production performance. `DataNodeFaultInjector` must be restored after delayed recovery; failure before restoration can poison later tests. Several scenarios assert exact block counts and generation stamp changes, so internal block lifecycle changes must preserve externally intended semantics or update tests deliberately. Snapshot tests are complex and encode multiple valid accounting branches depending on which snapshots remain.

Test signals: ready-vs-recovery return values, full-file byte comparisons after every truncate, content summary equals expected replicated bytes, snapshot path lengths remain readable, block map contains or excludes specific old/new blocks, generation stamp/block ID equality or inequality for in-place vs copy-on-truncate, lease holder switches to NameNode recovery, edit-log replay completes recovery, shell command exit status is zero, and quota usage matches content summary after snapshot deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileTruncate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsImageValidation.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsImageValidation.java

Purpose: `TestFsImageValidation` unit-tests the fsimage validation utility entry points: running validation when an image path is supplied by environment, HA configuration setup, and comma-separated number formatting.

Important APIs, types, and functions: it uses `FsImageValidation.initLogLevels`, `FsImageValidation.newInstance().run`, environment variable name `FsImageValidation.FS_IMAGE`, `FsImageValidation.setHaConf`, `HAUtil.isHAEnabled`, and `FsImageValidation.Util.toCommaSeparatedNumber`. Static initialization sets TRACE logging for `FsImageValidation`, `INodeReferenceValidation`, and `INode`.

Control flow: `testValidation` initializes log levels, attempts to run validation, and expects error count zero; if `FS_IMAGE_FILE` is not set and the utility throws `HadoopIllegalArgumentException`, the test logs a warning instead of failing. `testHaConf` sets HA config for namespace `cluster0` and asserts HA is enabled. `testToCommaSeparatedNumber` iterates many values below `Integer.MAX_VALUE`, formats them, and delegates to `runTestToCommaSeparatedNumber`, which validates digit/comma grouping and parses the value back.

State and persistence behavior: validation can read an external fsimage when the environment variable is set, but this test does not create one. Otherwise state is configuration mutation and pure formatting behavior.

Dependencies and integration points: depends on the standalone fsimage validation utility, HA configuration helpers, logging, and an optional environment-provided image file. It is an integration hook for manual validation runs inside the unit suite.

Risks and edge cases: `testValidation` can silently skip real validation when the environment variable is absent, so CI may only exercise the no-image path. The formatting loop is broad but limited to positive numbers under `Integer.MAX_VALUE`. Assertions around `s.length() % 4` encode comma grouping assumptions.

Test signals: zero validation errors when a provided image is validated, HA enabled after utility configuration, and formatted numbers contain only groups of up to three digits separated by commas and round-trip to the original value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsImageValidation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java

Purpose: `TestFsLimits` unit-tests NameNode namespace limits for maximum path component length and maximum directory item count, including mkdir and rename paths, disabled limits during edit-log loading, invalid configured limits, reserved `.snapshot` directory handling, and exception messages containing the correct parent directory.

Important APIs, types, and functions: it uses `DFS_NAMENODE_MAX_COMPONENT_LENGTH_KEY`, `DFS_NAMENODE_MAX_DIRECTORY_ITEMS_KEY`, `FSNamesystem.mkdirs`, `FSNamesystem.renameTo`, `Options.Rename`, `FSLimitException.PathComponentTooLongException`, `FSLimitException.MaxDirectoryItemsExceededException`, `HdfsConstants.DOT_SNAPSHOT_DIR`, mocked `FSImage`/`FSEditLog`, `NameNode.initMetrics`, and helper methods `getMockNamesystem`, `lazyInitFSDirectory`, `mkdirs`, `rename`, `deprecatedRename`, `mkdirCheckParentDirectory`, `renameCheckParentDirectory`, and `verify`.

Control flow: setup creates a fresh config with a NameNode directory URI, initializes metrics, and resets static `fs`/`fsIsReady`. Tests set limit values before the first operation, causing `lazyInitFSDirectory` to construct an FSNamesystem with those settings. Mkir and rename helpers execute the operation, catch any throwable, compare the generated exception class with the expected class, and return error text when needed. Rename coverage includes both modern `renameTo` with `Rename[]` and deprecated overload. `testDuringEditLogs` sets `fsIsReady=false`, proving component and directory limits are skipped while image/edit logs are loading except for reserved `.snapshot` validation.

State and persistence behavior: no disk persistence beyond configuration of a name-dir URI. The state under test is an in-memory FSNamesystem namespace and its image-loaded flag, which gates whether limits apply.

Dependencies and integration points: depends on FSNamesystem namespace mutation methods, reserved snapshot name validation, NameNode metrics setup, and exception message formatting.

Risks and edge cases: static fields (`conf`, `fs`, `fsIsReady`) make ordering safe only because `@BeforeEach` resets them. Helpers catch `Throwable`, which may hide assertion errors inside operations if expected is set incorrectly, though the class comparison usually exposes mismatches. Parent-directory verification tokenizes on whitespace, so formatting changes can affect it.

Test signals: expected exception class for overlong components, too many directory items, invalid limit values, reserved `.snapshot`; successful operations under limits; rename-specific failures at destination parent; limits disabled while `fsIsReady=false`; and error messages containing exact parent directory tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java -->
