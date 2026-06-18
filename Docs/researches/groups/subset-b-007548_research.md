# subset-b-007548 Research

Grouped source research for HDFS NameNode audit logging tests, authorization-context propagation tests, backup/checkpoint behavior, rack-aware block placement, block-under-construction state, cache-directive behavior, ViewDFS cache integration, and delegation-token checkpoint persistence. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogAtDebug.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogAtDebug.java

## Purpose

`TestAuditLogAtDebug` verifies that the default HDFS NameNode audit logger can suppress configured commands at INFO level and emit them only when the audit logger is at DEBUG. It targets `DFS_NAMENODE_AUDIT_LOG_DEBUG_CMDLIST` handling in `DefaultAuditLogger`/`FSNamesystemAuditLogger`.

## Important APIs, Types, and Functions

The class uses `FSNamesystem.FSNamesystemAuditLogger`, `DefaultAuditLogger.initialize`, `HdfsAuditLogger.logAuditEvent`, `GenericTestUtils.setLogLevel`, SLF4J `Level`, and Mockito `spy`/`verify`. `makeSpyLogger` builds an `HdfsConfiguration`, optionally sets the comma-separated debug command list, initializes the logger, sets `FSNamesystem.AUDIT_LOG` level, and returns a spy. `logDummyCommandToAuditLog` sends a minimal audit event with loopback address and no file status.

## Control Flow

Each test constructs a spy logger at INFO or DEBUG and sends one or two dummy commands. Commands listed in the debug command list should not call `logAuditMessage` when the audit log is at INFO, but should call it at DEBUG. Commands not listed remain normal INFO audit messages. With no configured debug command list, both dummy commands log at INFO.

## State and Persistence Behavior

State is limited to the in-memory logger configuration and the global audit logger log level. No filesystem or edit-log persistence is exercised. The debug command list is parsed from configuration during `initialize`, so tests validate initialization-time state rather than live reconfiguration.

## Dependencies and Integration Points

The file depends on HDFS configuration keys, `HdfsConfiguration`, the NameNode audit logger, Java `Inet4Address`, Guava `Joiner`, JUnit 5 timeout/tests, and Mockito. It integrates with the same `FSNamesystem.AUDIT_LOG` category used by production NameNode auditing.

## Risks and Edge Cases

Because the test changes a shared logger level, ordering with other audit-log tests can matter if tests run in the same JVM without reset. The command matching is direct string matching; whitespace, case, and command-name normalization are not covered. It only verifies the final call/no-call decision to `logAuditMessage`, not the exact rendered message.

## Test Signals

The key signals are `never()` for configured debug commands at INFO, `times(1)`/`times(2)` for configured debug commands at DEBUG, logging of non-debug commands at INFO, handling of multiple configured commands, and behavior when no command list is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogAtDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogger.java

## Purpose

`TestAuditLogger` validates the custom `AuditLogger` extension point and the default audit-log text path around WebHDFS, ACLs, caller context, remote ports, and audit logger failure propagation. It ensures NameNode audit events carry the expected command, source, permissions, remote address, and optional caller metadata.

## Important APIs, Types, and Functions

The tests configure `DFS_NAMENODE_AUDIT_LOGGERS_KEY`, `NNTOP_ENABLED_KEY`, `DFS_NAMENODE_AUDIT_LOG_WITH_REMOTE_PORT_KEY`, `DFS_NAMENODE_ACLS_ENABLED_KEY`, and caller-context keys. `DummyAuditLogger` implements `AuditLogger`, records initialization, log counts, unsuccessful counts, found permission, remote address, and last command. `BrokenAuditLogger` throws from `logAuditEvent` for most commands. The class uses `MiniDFSCluster`, `FileSystem`, `DFSTestUtil`, WebHDFS `HttpURLConnection`, `ProxyServers`, `ProxyUsers`, `CallerContext`, `SubjectInheritingThread`, ACL APIs, and `LogCapturer`.

## Control Flow

The setup resets static `DummyAuditLogger` fields and refreshes proxy-user configuration. Basic logger tests start a cluster with the dummy logger, execute filesystem operations such as `setTimes`, and assert audit events reached the custom logger. WebHDFS tests issue HTTP requests with and without `X-Forwarded-For`, first without trusted proxy settings and then after configuring `ProxyServers`, to prove the audit address switches only for trusted proxies. Caller-context tests set current contexts, signatures, long strings, invalid contexts, and child-thread contexts before filesystem calls, then check the captured audit line suffix. ACL tests call both successful and failing ACL APIs and FS shell commands, checking log counts and unsuccessful counts. Broken logger tests ensure audit logger exceptions fail requests. Remote-port and escape tests inspect raw audit text patterns.

## State and Persistence Behavior

The class uses static fields in `DummyAuditLogger` as test-observable audit state. Cluster state is transient MiniDFSCluster namespace state, with ACL bits and permissions mutated for audit behavior. No edit-log recovery is the main target, but operations are real NameNode RPCs and therefore flow through normal namespace mutation and audit paths. Caller context is thread-local/inheritable state and must be cleared or overwritten by each scenario.

## Dependencies and Integration Points

Integration points include `FSNamesystem` audit logger registration, NNTOP logger injection, WebHDFS request handling, proxy-server trust evaluation, HDFS ACL commands, FS shell `-getfacl` behavior, `CallerContext` propagation through IPC, and formatted audit text generated by `DefaultAuditLogger`. Mockito is used to replace `FSDirectory.checkTraverse` with an ACL failure source.

## Risks and Edge Cases

Static logger fields make tests sensitive to reset discipline. WebHDFS assertions depend on loopback address and local HTTP behavior. Caller-context tests depend on exact truncation, signature length handling, newline/tab escaping, and thread inheritance semantics. `BrokenAuditLogger` verifies fail-fast behavior, so production changes that isolate logger failures would intentionally break that signal. ACL shell count assertions are brittle if FS shell starts making additional metadata calls.

## Test Signals

Signals include dummy logger initialization, expected log-count increments, unsuccessful count increments for ACL failures, captured permission after `setPermission`, `lastCommand=getfileinfo` for WebHDFS, trusted proxy remote address switching from `127.0.0.1` to forwarded address, audit lines ending in caller-context strings, remote-port pattern matching with `clientPort`, escaped newline/tab caller text, and a `RemoteException` when a custom logger throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLoggerWithCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLoggerWithCommands.java

## Purpose

`TestAuditLoggerWithCommands` is a broad command-name coverage suite for NameNode audit logging. It verifies that successful and failed administrative, namespace, cache, snapshot, xattr, delegation-token, safe-mode, reconfiguration, and storage-management operations emit audit entries with the intended `cmd=` value and allowed flag.

## Important APIs, Types, and Functions

The fixture builds a secure/permission-enabled `MiniDFSCluster` with ACLs, delegation-token always-use, and service authorization enabled. It creates two test users, captures `FSNamesystem.AUDIT_LOG`, keeps `NamenodeProtocols proto`, and uses `DFSTestUtil.getFileSystemAs`. Important helpers are `verifyAuditLogs(String)`, `verifyAuditLogs(boolean, String)`, `verifySetQuota`, safe-mode helpers, restore-failed-storage helpers, and `removeExistingCachePools`. The tests call `DistributedFileSystem`, `FileSystem`, `NameNodeRpcServer`, `FSNamesystem`, and delegation-token APIs.

## Control Flow

Each test arranges namespace or administrative state, performs one operation as an unauthorized or authorized user, catches the expected `AccessControlException` or `IOException`, and validates the last audit log line with a regex. For many operations it closes a `FileSystem` and reruns the call to ensure client-side closed-filesystem failures do not produce new audit entries. RPC-administrative tests synthesize `Server.Call` with a remote user and mark invocations as external so `FSNamesystem` permission checks and audit paths are exercised for admin commands.

## State and Persistence Behavior

The suite mutates namespace permissions, ownership, snapshots, cache pools/directives, encryption-zone lookup inputs, delegation token lifecycle, rolling-upgrade metadata, safe-mode state, edit-log roll state, failed-storage setting, and datanode reports. State is per-test cluster state and cleaned up in `tearDown` by clearing `Server.getCurCall`, closing filesystems, and shutting down the cluster. Delegation-token tests persist token state only within the running cluster and assert audit events for get/renew/cancel success and failure.

## Dependencies and Integration Points

The file integrates with HDFS permission checking, cache manager RPCs, snapshot manager, delegation-token secret manager, NameNode admin RPC server, `FSNamesystem` admin methods, `Server.Call` IPC context, `RPC.RpcKind`, `DatanodeStorageReport`, and audit text formatting. It also uses Mockito spies to control remote users and external-invocation flags.

## Risks and Edge Cases

The test suite is sensitive to exact command names such as `contentSummary`, `setQuota`, `createSnapshot`, `addCache`, `safemode_force_exit`, `getDatanodeStorageReport`, and `reportBadBlocks`. Audit-count assertions can break if new audit events are added to failure paths. Tests that close filesystems deliberately distinguish server-side authorization logging from local client failures. Synthetic `Server.Call` setup must be kept in sync with IPC behavior to remain representative.

## Test Signals

Signals cover denied audit entries for content summary, quota, concat, snapshots, cache directives/pools, quota usage, EZ lookup, rename, xattr get, ACL status, and delete-root. Successful admin signals include metaSave, reconfiguration, refresh commands, rolling-upgrade query/finalize, rollEditLog, safe-mode actions, balancer bandwidth, refreshNodes, finalizeUpgrade, saveNamespace, datanode reports, restoreFailedStorage variants, and reportBadBlocks. Delegation-token signals validate success and failure audit lines for get, renew, and cancel with token source text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLoggerWithCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogs.java

## Purpose

`TestAuditLogs` verifies that standard HDFS and WebHDFS file operations generate correctly shaped NameNode audit log lines for allowed and denied access. It runs under both synchronous and asynchronous edit logging configurations.

## Important APIs, Types, and Functions

The class is a JUnit parameterized class over `useAsyncEdits`. It uses `MiniDFSCluster`, `DFSTestUtil`, `FileSystem`, `WebHdfsFileSystem`, `WebHdfsTestUtil`, `UserGroupInformation`, `LogCapturer`, log4j `AsyncAppender`, and regex patterns for audit format, success/failure, and WebHDFS open protocol. Helpers `verifySuccessCommandsAuditLogs` and `verifyFailedCommandsAuditLogs` scan captured audit output for matching `allowed=`, file path, and command text.

## Control Flow

`setupCluster` configures access-time precision, block reports, and async edit logging, creates a four-datanode cluster, populates test files, verifies the audit log appender is asynchronous, and creates a test UGI. Tests perform allowed HDFS open/stat, denied HDFS open, allowed WebHDFS open/stat, denied WebHDFS open, and a create using a path containing carriage-return/newline. Each scenario then scans the accumulated audit capture for required success or failure counts.

## State and Persistence Behavior

The test creates real files under `/srcdat`, changes permissions and ownership to force access outcomes, and cleans the namespace after each parameter run. Async edit logging is a NameNode configuration dimension rather than a separate persistence assertion; the tests verify audit logging remains present with the configured edit-log mode. Audit capture is static across the class and stopped after all tests.

## Dependencies and Integration Points

It integrates with `FSNamesystem.AUDIT_LOG`, log4j audit appenders, HDFS permission enforcement, WebHDFS protocol command mapping, test UGI filesystem creation, and path escaping in audit output. The expected audit line format includes `allowed`, `ugi`, `ip`, `cmd`, `src`, `dst`, and `perm`.

## Risks and Edge Cases

Because the capture is cumulative, helper counts use minimum counts for success paths and exact counts for failure paths. WebHDFS open can generate multiple audit entries, so the expected minimum differs from native HDFS. The CRLF path test checks that a malicious path does not inject raw newlines into audit output, but it only asserts matching on the `foo` prefix.

## Test Signals

Important signals are two native success audit lines for open/stat, one denied native open line, WebHDFS success lines including `cmd=open`/`cmd=getfileinfo`, one denied WebHDFS open line, `AUDIT_PATTERN` conformance, and successful create logging for a path containing `\r\n` without newline injection into the parsed audit stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationContext.java

## Purpose

`TestAuthorizationContext` verifies the new `INodeAttributeProvider.AuthorizationContext` builder and the compatibility bridge between legacy `AccessControlEnforcer.checkPermission` and `checkPermissionWithContext` in `FSPermissionChecker`.

## Important APIs, Types, and Functions

The test uses `CallerContext`, `UserGroupInformation`, mocked `INodesInPath`, `INodeAttributeProvider`, and `AccessControlEnforcer`. It exercises `AuthorizationContext.Builder` setters for filesystem owner, supergroup, caller UGI, inode attributes, inode array, path components, snapshot ID, path, ancestor index, owner/access flags, operation name, and caller context. It also uses `FSPermissionChecker.setOperationType`.

## Control Flow

`setUp` programs the mocked `INodesInPath` to return empty inode/path state. `testBuilder` populates a builder, builds a context, and asserts getters return the exact configured values. `testLegacyAPI` configures a permission checker with context API disabled, invokes `checkPermission`, and verifies the old `checkPermission` signature is called. `testCheckPermissionWithContextAPI` enables the context API, sets an operation type, invokes `checkPermission`, builds an expected context, and verifies `checkPermissionWithContext` is used.

## State and Persistence Behavior

There is no filesystem persistence. State is mock-returned path metadata plus thread-local `CallerContext` and static operation type state in `FSPermissionChecker`. The tests validate object assembly and dispatch, not on-disk namespace changes.

## Dependencies and Integration Points

The file sits at the integration boundary between `FSPermissionChecker`, `INodeAttributeProvider`, external authorization enforcers, inode path metadata, and caller-context propagation. It ensures newer context-aware authorization hooks can coexist with legacy implementations.

## Risks and Edge Cases

The expected `ancestorIndex` is `inodes.length - 2`, which is `-2` for the empty inode array used here; production callers usually have real paths. The verification relies on `AuthorizationContext.equals` accepting another context object broadly, so it proves API selection more than deep object equality in the Mockito verification. Static operation type and caller context need cleanup discipline in broader suites.

## Test Signals

Signals include getter equality for every builder field, Mockito verification of the legacy `checkPermission` argument list when the context API flag is false, and Mockito verification of `checkPermissionWithContext` when the flag is true and an operation name has been set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationHeaderPropagation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationHeaderPropagation.java

## Purpose

`TestAuthorizationHeaderPropagation` verifies that per-RPC authorization-header bytes stored in `AuthorizationContext` are visible to NameNode audit loggers and do not leak across subsequent RPCs after clearing.

## Important APIs, Types, and Functions

The nested `HeaderCapturingAuditLogger` implements `AuditLogger` and reads `AuthorizationContext.getCurrentAuthorizationHeader()` inside `logAuditEvent`, storing a defensive byte-array copy or null. The test configures `DFS_NAMENODE_AUDIT_LOGGERS_KEY`, starts `MiniDFSCluster`, uses `AuthorizationContext.setCurrentAuthorizationHeader`, `AuthorizationContext.clear`, and performs `FileSystem.mkdirs` calls.

## Control Flow

The test clears captured headers, sets `header-one`, makes a mkdir RPC, clears context, sets `header-two`, makes a second mkdir RPC, clears again, then makes a third mkdir with no header. It asserts the first two audit events captured the corresponding byte arrays and the third captured null.

## State and Persistence Behavior

Header state is per-thread/per-RPC context state, copied by the audit logger to avoid later mutation. Namespace state consists only of three created directories. No edit-log recovery or long-lived persistence is validated.

## Dependencies and Integration Points

The file integrates Hadoop security `AuthorizationContext` with `FSNamesystem` audit logger invocation and custom audit logger configuration. It relies on the NameNode audit path executing during each `mkdirs` RPC.

## Risks and Edge Cases

The nested logger uses a static list that must be cleared before assertions. The test assumes one audit event per mkdir and inspects fixed list indexes. It does not test concurrent RPCs or mutation of the caller-provided byte array after setting the context, although the logger itself copies what it observes.

## Test Signals

The decisive signals are `assertArrayEquals(header1, capturedHeaders.get(0))`, `assertArrayEquals(header2, capturedHeaders.get(1))`, and `assertNull(capturedHeaders.get(2))`, proving both propagation and explicit clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationHeaderPropagation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBackupNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBackupNode.java

## Purpose

`TestBackupNode` validates HDFS BackupNode and CheckpointNode behavior: startup state, checkpoint upload, edit-log tailing, storage-directory equivalence, authentication failure handling, read/write restrictions, crash handling, and reading data through a backup node.

## Important APIs, Types, and Functions

Key helpers include `getBackupNodeDir`, `startBackupNode`, `waitCheckpointDone`, `testBNInSync`, `assertStorageDirsMatch`, and `testCheckpoint`. The class uses `NameNode.createNameNode`, `BackupNode`, `BackupImage`, `Checkpointer`, `FSImageTestUtil`, `FileJournalManager.EditLogFile`, `StorageDirectory`, `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `NamenodeProtocols.rollEditLog`, `DFSTestUtil`, and HA/backup configuration keys such as `DFS_NAMENODE_BACKUP_ADDRESS_KEY` and backup HTTP address.

## Control Flow

`setUp` deletes the MiniDFSCluster base directory and prepares checkpoint/backup name directories. `startBackupNode` configures name and edits dirs, starts a NameNode in checkpoint or backup role, and asserts safe mode plus standby HA state. `startBackupNodeWithIncorrectAuthentication` starts a simple-auth primary, switches backup config to Kerberos with invalid keytab, and expects an IOException rather than a null-pointer abort. Checkpoint tests create namespace edits, start a checkpoint/backup node, wait until the active NameNode records a checkpoint at or beyond a txid, compare storage dirs, restart without formatting, and repeat checkpoints.

## State and Persistence Behavior

This file is heavily persistence-oriented. It verifies fsimage checkpoint transfer to the active NameNode, in-progress edits behavior during BackupNode shutdown, namespace survival across non-format restarts, deletion persistence (`file1` removed while `file2` remains), and identical name/current directories excluding `VERSION`. The tailing test confirms a BackupNode receives edits as files are created, rolls edit logs with the active, uploads checkpoint images, restarts from storage, and tolerates unclean backup-node stop while active edits continue.

## Dependencies and Integration Points

Integration points include active NameNode edit logging, backup node edit tailing, checkpoint image upload, HA standby reads, NameNode RPC addresses, DataNode HA-style dual NameNode config for backup reads, security authentication setup, and filesystem clients pointed at backup-node RPC addresses. `FSImageTestUtil` provides the main storage-level assertions.

## Risks and Edge Cases

The tests depend on local ports, filesystem cleanup, and timing loops for checkpoint completion and edit tailing. Authentication regression coverage checks the error message contains `Running in secure mode`. The read/write behavior differs by role: BackupNode may serve reads, CheckpointNode may not, and writes through backup-node RPC must fail. The final tailing test has a risky-looking `assertStorageDirsMatch(cluster.getNameNode(), backup)` after backup can be nulled in the finally path; the assertion executes after cleanup and depends on the retained object state from the try path.

## Test Signals

Signals include backup/checkpoint startup in safe mode/standby, `FSImageTestUtil.assertNNHasCheckpoints`, identical storage dirs excluding `VERSION`, current segment txid matching after `rollEditLog`, backup namespace visibility for created paths, latest edit log remaining in-progress after backup stop, no active failure after unclean backup stop, failed writes to backup, role-dependent backup reads, matching data read through active and backup node, and token-authentication startup failure avoiding NPE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBackupNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockPlacementPolicyRackFaultTolerant.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockPlacementPolicyRackFaultTolerant.java

## Purpose

`TestBlockPlacementPolicyRackFaultTolerant` validates `BlockPlacementPolicyRackFaultTolerant` target selection across racks, including normal replication, additional datanode requests for existing blocks, and decommission scenarios where some racks have only one node.

## Important APIs, Types, and Functions

The setup configures `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` to `BlockPlacementPolicyRackFaultTolerant`, sets block/checksum sizes, starts 20 datanodes across 10 racks, and captures `NamenodeProtocols`, `FSNamesystem`, and `PermissionStatus`. Main helpers are `doTestChooseTargetNormalCase`, `doTestChooseTargetSpecialCase`, `shuffle`, `doTestLocatedBlock`, `doTestLocatedBlockRacks`, and `addToRacksCount`. The decommission test uses `DFSNetworkTopology`, `BlockManager`, `DatanodeManager`, datanode admin manager, erasure-coding policy setup, and `verifyBlockPlacement`.

## Control Flow

Normal choose-target testing creates multiple files with varying base replication and additional replication. It calls `namesystem.startFile`, `nameNodeRpc.addBlock`, and `nameNodeRpc.getAdditionalDatanode`, then verifies the located block contains the requested number of targets and rack counts differ by at most one. The special-case flow creates a 20-replica block, repeatedly shuffles partial existing locations, asks for additional datanodes, and checks the merged target set remains rack-balanced. The decommission flow starts a smaller DFS network topology, decommissions the client rack's only node, creates a striped-policy file, verifies target racks avoid the decommissioned rack and use four valid racks, then decommissions another single-rack node and verifies block-placement satisfaction.

## State and Persistence Behavior

State is in-memory MiniDFSCluster datanode topology, NameNode block target selection, datanode decommission state, and created file/block metadata. No restart or edit-log persistence is tested. The decommission path uses NameNode write locking around admin-manager state changes and waits for decommission completion before checking located blocks.

## Dependencies and Integration Points

The test integrates block placement policy configuration, NameNode file creation and add-block RPCs, additional-datanode selection, DFS network topology, datanode decommission management, erasure coding policy enablement, and striped block placement verification. Static rack mapping is reset before setup to avoid prior tests influencing topology.

## Risks and Edge Cases

Rack balance is asserted by count difference rather than exact target identity, making the test robust to target ordering but sensitive to topology assumptions. The special-case shuffle specifically protects against repeatedly choosing racks that already have more replicas when empty racks are available. Decommission timing can be asynchronous and relies on `GenericTestUtils.waitFor`. The decommission test reassigns `cluster` after shutting down the default fixture cluster, so teardown must tolerate that replacement.

## Test Signals

Signals include exact target counts for all replication/additional-replication cases, max rack-count minus min rack-count at most one, expected valid rack count of four under decommission, two replicas on `/RACK0` and `/RACK2` after additional placement, successful decommission completion, and `BlockPlacementStatus.isPlacementPolicySatisfied()` for located blocks after topology reduction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockPlacementPolicyRackFaultTolerant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockUnderConstruction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockUnderConstruction.java

## Purpose

`TestBlockUnderConstruction` verifies NameNode metadata consistency for files being written, block-location reads against unclosed files, and block recovery behavior when expected storage IDs no longer resolve.

## Important APIs, Types, and Functions

The class uses a static `MiniDFSCluster` with three datanodes, `DistributedFileSystem`, `FSDataOutputStream`, `DFSClientAdapter`, `NamenodeProtocols.getBlockLocations`, `FSNamesystem`, `INodeFile`, `BlockInfo`, `BlockManager`, `BlockUnderConstructionFeature`, `BlockUCState`, and `commitBlockSynchronization`. Helpers `writeFile` and `verifyFileBlocks` drive block allocation and inspect NameNode internal block state.

## Control Flow

`writeFile` writes a full block using `TestFileCreation.writeFile`, flushes to datanodes, and polls client block locations until the block count increases. `verifyFileBlocks` looks up the inode, checks whether it is under construction as expected, walks all blocks, asserts all but the trailing blocks are complete and registered in the BlocksMap, and checks last-block completion after close. `testBlockCreation` writes five blocks to an open file, verifying consistency after each write and after close. `testGetBlockLocations` writes an unclosed file incrementally and asserts the last returned block is not complete. `testEmptyExpectedLocations` fakes block recovery with an invalid storage ID and verifies subsequent block-location lookup does not throw.

## State and Persistence Behavior

The suite targets live NameNode metadata state: inode under-construction flag, block completion/committed states, BlocksMap identity, located-block responses, generation stamps, and recovery metadata. There is no restart persistence. The invalid-storage scenario models storage failure or datanode reregistration by supplying a nonexistent storage ID during synchronization.

## Dependencies and Integration Points

It integrates client writes/DataStreamer allocation, NameNode block manager internals, inode directory lookup, block recovery initialization, and NameNode RPC block-location APIs. It uses `TestFileCreation` utilities to match expected block size behavior.

## Risks and Edge Cases

The `writeFile` helper ignores its `size` parameter and always writes `BLOCK_SIZE`, so callers passing half-block length still create full-block write behavior while using `len` as the query length. The penultimate-block assertion contains complex boolean logic and is mainly a regression guard for committed/complete transitions. The invalid-storage test tolerates a current `IllegalStateException`, focusing only on avoiding later NPE in block-location lookup.

## Test Signals

Signals include inode `isUnderConstruction` matching file-open state, all inspected blocks present by identity in BlocksMap, closed-file last block complete, unclosed-file final located block incomplete, no crash after `commitBlockSynchronization` with `invalid-storage-id1`, and successful subsequent `getBlockLocations`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockUnderConstruction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectives.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectives.java

## Purpose

`TestCacheDirectives` is the main NameNode cache-manager integration suite. It validates cache pool CRUD, cache directive CRUD, permissions, limits, expirations, cache replication and reporting, fsimage/edit-log restart behavior, HA standby expiry consistency, behavior when caching is disabled, and capacity/no-backing-replica edge cases.

## Important APIs, Types, and Functions

The fixture configures cache-related keys through `createCachingConf`: block size, datanode locked memory, heartbeat interval, cache report interval, path-based cache refresh interval, and list batching limits. It uses `MiniDFSCluster`, `DistributedFileSystem`, `NamenodeProtocols`, `NameNode`, `CacheManager`, `CachePoolInfo`, `CachePoolEntry`, `CachePoolStats`, `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CacheDirectiveStats`, `CacheDirectiveIterator`, `CacheFlag`, `Expiration`, `SecondaryNameNode`, `DataNodeTestUtils`, `BlockReaderTestUtil`, `NativeIO.POSIX.NoMlockCacheManipulator`, and HA utilities. Helpers include `validateListAll`, `addAsUnprivileged`, `waitForCachedBlocks`, `waitForCacheDirectiveStats`, `waitForCachePoolStats`, `checkNumCachedReplicas`, `checkPendingCachedEmpty`, and overridable `getDFS` methods.

## Control Flow

Setup starts a four-datanode cluster with stubbed mlock and caching tracing enabled. Teardown removes all directives, waits for cached blocks to drop to zero, shuts down the cluster, and restores the previous `CacheManipulator`. Pool tests add, modify, list, and remove pools while validating duplicate, empty, null, nonexistent, and closed-filesystem failures. Directive tests create multiple pools with different modes, add directives as an unprivileged user, verify ID uniqueness and filtered listing, reject malformed paths and inaccessible/unknown pools, remove and modify directives, and check closed-filesystem failures.

## State and Persistence Behavior

The cache manager state under test includes pool metadata, directive metadata and IDs, max relative expiry, per-directive and per-pool stats, cached-block membership, datanode cached/pending lists, cache capacity/used counters, and fsimage/edit-log serialization. `testCacheManagerRestart` checkpoints with a `SecondaryNameNode`, saves namespace, restarts the NameNode, verifies pools/directives/expiry survive, and ensures the next directive ID advances from the previous persisted ID. `testExpiryTimeConsistency` uses an HA topology, modifies directive expiry on the active, waits for the standby to tail edits, and compares active/standby `CacheDirective.getExpiryTimeString()` under FS read locks.

## Dependencies and Integration Points

This suite integrates NameNode cache RPCs, DFS client convenience APIs, permission checking for cache pools, datanode cache reports, block-location cached-host advertisement, secondary NameNode checkpointing, fsimage save/load, HA edit tailing, datanode capacity accounting, cache monitor scheduling, and `NativeIO` mlock abstraction. `TestCacheDirectivesWithViewDFS` extends this class to run the same behavior through ViewDFS-backed `DistributedFileSystem` instances.

## Risks and Edge Cases

The tests are timing-sensitive because cache reports, heartbeats, path-based refresh, and HA tailing are asynchronous. Several helper waits use 60-120 second timeouts. Capacity tests depend on the fake `NoMlockCacheManipulator` and fixed `CACHE_CAPACITY`. Permission tests distinguish pool visibility from full metadata visibility. Force flags intentionally bypass pool limit failures. Expiry assertions compare wall-clock-derived values with tolerances. Caching-disabled tests assert directives can be added without creating cache replication work or monitor state.

## Test Signals

Important signals include expected exception messages for invalid pool/directive inputs, exact directive ID listing order, partial versus full pool info based on permissions, persisted pool/directive metadata after checkpoint/restart, cached block and replica counts reaching expected values, datanode cache capacity equaling used plus remaining, directory directive stats and pool stats matching bytes/files needed/cached, replication factor step-up/step-down visible in cached hosts, expired directives dropping cached blocks, overlimit bytes accounting, no pending cached entries for over-capacity blocks, cached replica count dropping after backing replicas are removed, no located-block interactions when cache is unused, zero cached blocks when caching is disabled, and matching active/standby expiry strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectives.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectivesWithViewDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectivesWithViewDFS.java

## Purpose

`TestCacheDirectivesWithViewDFS` reruns the `TestCacheDirectives` suite through `ViewDistributedFileSystem` to verify cache-directive and cache-pool behavior works when HDFS is accessed through ViewDFS link and fallback configuration.

## Important APIs, Types, and Functions

The class extends `TestCacheDirectives` and overrides `getDFS()` and `getDFS(MiniDFSCluster, int)`. It sets `fs.hdfs.impl` to `ViewDistributedFileSystem`, reads the default HDFS URI from `CommonConfigurationKeys.FS_DEFAULT_NAME_KEY` or `cluster.getURI(0)`, and configures ViewFS with `ConfigUtil.addLinkFallback` plus an explicit `/tmp` link.

## Control Flow

The inherited base setup calls `getDFS`, so this subclass injects ViewDFS configuration before returning the filesystem. For HA/restart helper use, the cluster-indexed override updates the NameNode-specific configuration and returns `cluster.getFileSystem(0)` after setting ViewDFS mappings. All actual test methods, waits, and assertions are inherited from `TestCacheDirectives`.

## State and Persistence Behavior

No new persistence is introduced beyond the base cache-directives suite. The additional state is configuration-level ViewDFS mount/fallback mapping that rewrites how client paths reach the underlying HDFS namespace. Cache pool/directive state, stats, cached blocks, checkpoints, and HA expiry behavior remain stored in the underlying NameNode cache manager.

## Dependencies and Integration Points

The subclass integrates ViewDFS path resolution with `DistributedFileSystem` cache APIs, ViewFS fallback links, explicit `/tmp` mount links, MiniDFSCluster configuration, and all inherited NameNode cache-manager RPC paths.

## Risks and Edge Cases

Because it inherits a broad suite, failures may stem from ViewDFS path qualification rather than cache-manager logic. The overrides mutate shared configuration keys, so ordering with other tests using the same configuration object matters. The explicit `/tmp` link plus fallback covers common path resolution but does not test multiple mount tables or non-default nameservices.

## Test Signals

The signal is successful execution of the inherited `TestCacheDirectives` methods using ViewDFS-configured clients. In particular, relative path qualification, directive path listing, HA expiry consistency, and checkpoint/restart cache-manager state must behave identically to direct HDFS access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectivesWithViewDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckPointForSecurityTokens.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckPointForSecurityTokens.java

## Purpose

`TestCheckPointForSecurityTokens` verifies that delegation-token secret-manager state survives `saveNamespace` checkpoints and repeated NameNode restarts, allowing previously issued tokens to be renewed and canceled after image reloads.

## Important APIs, Types, and Functions

The class uses `MiniDFSCluster`, `DistributedFileSystem`, `FSNamesystem.getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, `DFSAdmin -saveNamespace`, `SafeModeAction.ENTER`, `FSImageTestUtil.findLatestEditsLog`, `FileJournalManager.EditLogFile`, `StorageDirectory`, `DelegationTokenIdentifier`, and `Token`. Configuration enables `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`.

## Control Flow

`testSaveNamespace` starts a three-datanode cluster, obtains two delegation tokens, inspects each storage directory's latest in-progress edits log and expects five transactions, enters safe mode, runs `DFSAdmin -saveNamespace`, then verifies the latest in-progress edit log has only the start transaction. It restarts without formatting, renews the original tokens, creates additional tokens, restarts again, renews all known tokens, creates one more token, restarts a third time, and finally renews and cancels all tokens.

## State and Persistence Behavior

The core state is delegation-token metadata persisted from edit logs into fsimage during `saveNamespace` and replayed across non-format restarts. The test also verifies edit-log rolling/truncation behavior around saveNamespace by counting transactions before and after the checkpoint. Tokens issued after the checkpoint must persist through subsequent edit-log replay and image reloads.

## Dependencies and Integration Points

It integrates NameNode delegation-token secret manager, FSImage storage directories, edit-log scanning, DFSAdmin safe-mode saveNamespace command, MiniDFSCluster restart with `format(false)`, and login-user renewer identity. Token operations are invoked directly through the namesystem rather than through a DFS client token-renewal service.

## Risks and Edge Cases

Transaction count expectations are exact and can change if token issuance or saveNamespace writes additional edits. The test assumes the login user can renew all issued tokens. Failures in either renew or cancel are collapsed into broad fail messages, so debugging often requires checking the preceding token lifecycle step. The saveNamespace operation must be run in safe mode; the comment says saving outside safe mode should fail, but the test only verifies edit-log state before entering safe mode.

## Test Signals

Signals include five transactions in the pre-save in-progress edit log, one start transaction after saveNamespace, successful renewals of tokens issued before and after restarts, and successful final renew/cancel of all five tokens after repeated non-format cluster restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckPointForSecurityTokens.java -->
