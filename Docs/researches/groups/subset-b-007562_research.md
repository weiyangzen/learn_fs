# subset-b-007562 Research

Grouped research for the listed Hadoop HDFS test files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/sps/TestExternalStoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/sps/TestExternalStoragePolicySatisfier.java

## Purpose
`TestExternalStoragePolicySatisfier` is a slow JUnit 5 integration suite for external HDFS Storage Policy Satisfier (SPS). It verifies that an out-of-NameNode SPS process can consume `satisfyStoragePolicy` requests, schedule block storage movements, honor storage-policy semantics such as `COLD`, `ALL_SSD`, `ALL_NVDIMM`, `ONE_SSD`, and `WARM`, recover across NameNode/DataNode restarts, and expose metrics. It also covers Kerberos/keytab startup, queue limits, mover-ID exclusivity, erasure-coded file rejection/cleanup, empty and deleted paths, low/excess redundancy, block pinning, and JMX publication.

## Important APIs, Types, And Functions
The fixture owns a `HdfsConfiguration`, `MiniDFSCluster`, `DistributedFileSystem`, `NameNodeConnector`, `StoragePolicySatisfier`, and `ExternalSPSContext`. `setUp()` forces `DFS_STORAGE_POLICY_SATISFIER_MODE_KEY` to `EXTERNAL` and shortens the SPS DataNode cache refresh. `startCluster(...)` builds multi-storage MiniDFS clusters with configurable `StorageType[][]`, per-storage capacity, and optional mover-ID creation; when `startSPS` is true it creates the `NameNodeConnector`, initializes `ExternalSPSContext`, and starts `StoragePolicySatisfier` in external mode. `restartNamenode()`, `startExternalSps()`, and `stopExternalSps()` are the main lifecycle controls.

The major public test APIs exercised are `DistributedFileSystem.setStoragePolicy`, `DistributedFileSystem.satisfyStoragePolicy`, `HdfsAdmin.satisfyStoragePolicy`, `DFSTestUtil.waitExpectedStorageType`, `DFSTestUtil.waitForXattrRemoved`, `NameNodeProxies.createProxy(... ClientProtocol.class)`, MiniDFSCluster DataNode restart/start APIs, and `ExternalSPSBeanMetrics`/JMX attributes. Helper methods include `writeContent`, `startAdditionalDNs`, `createDirectoryTree`, `getDFSListOfTree`, `createFileAndSimulateFavoredNodes`, `waitForAttemptedItems`, and `waitForBlocksMovementAttemptReport`.

## Control Flow
Most tests follow the same flow: configure a cluster with initial DISK replicas, write one or more files, set a storage policy, add DataNodes with the target storage type if needed, call `satisfyStoragePolicy`, trigger heartbeats, then wait for expected storage-type counts or SPS attempted-item counters. Tests that stop SPS deliberately create pending NameNode-side xattrs/queues, then restart external SPS to confirm it skips deleted work and continues processing new work.

Several tests alter the default flow. `testWithKeytabs` builds a MiniKdc and runs a normal SPS movement inside a keytab-authenticated UGI. `testOutstandingQueueLimitExceeds` stops SPS before submitting requests to force an outstanding queue-limit exception. `testInfiniteStartWhenAnotherSPSRunning` uses the mover-ID path and `ExitUtil` to verify that a second external SPS instance exits. `testSPSShouldNotLeakXattrIfSatisfyStoragePolicyCallOnECFiles` uses `ClientProtocol` to configure EC and asserts unsuitable `ONE_SSD` requests leave no satisfy xattr. Redundancy tests stop/restart DataNodes or reduce replication before policy satisfaction. Metrics tests either inspect NameSystem pending paths or register metrics and query `Hadoop:service=ExternalSPS,name=ExternalSPS` via the platform MBeanServer.

## State And Persistence Behavior
Persistent HDFS state under test includes block replicas, storage policy IDs, satisfy-storage-policy xattrs, edit-log transaction IDs, mover-ID files, EC policy metadata, replication factors, and NameNode SPS queues. External SPS itself maintains processing queues, attempted item monitors, retry state, and metrics counters; tests observe these through `BlockStorageMovementAttemptedItems` and JMX. Kerberos state is local to a temporary MiniKdc base directory and keytab, cleaned in `destroy()`. The suite intentionally restarts NameNodes/DataNodes to prove storage-policy requests and block state survive process boundaries and that stale or empty work is cleaned from NameNode metadata.

## Dependencies And Integration Points
This test is tightly integrated with HDFS internals: `MiniDFSCluster`, DataNode test hooks (`DataNodeTestUtils`, `InternalDataNodeTestUtils`), `NameNodeConnector`, `StoragePolicySatisfier`, `ExternalSPSContext`, NameNode edit logs/INodes, `BlockStorageMovementAttemptedItems`, `HdfsAdmin`, `ClientProtocol`, EC utilities, MiniKdc, SSL test utilities, and JMX. It also depends on heartbeat and SPS recheck timing, block movement reporting via DataNode heartbeats, and storage-type-aware block placement and movement code.

## Risks And Edge Cases
The suite is timing-sensitive because movement, heartbeat, and retry detection are asynchronous; most tests rely on `GenericTestUtils.waitFor` or `DFSTestUtil.waitExpectedStorageType` with long timeouts. Storage-capacity and target-selection assertions are fragile if placement policies change. Security tests mutate global UGI and Kerberos realm state, so `finally` reset is important. Several internal-SPS tests are disabled because external SPS has different traversal/batching semantics. The EC xattr and zero-length file tests protect against metadata leaks and unnecessary edit-log writes. Block-pinning and low/excess redundancy cases protect scheduling logic from moving invalid replicas or misclassifying redundancy states.

## Test Signals
Strong success signals are exact storage-type replica counts after movement, expected attempted-item counts, queue-limit exception text, absence or removal of satisfy xattrs, no edit-log transaction change for zero-length files, JMX attributes moving from zero to one, and successful keytab-based execution. Failure modes usually surface as timeout waiting for movement, stale queue counts, unexpected xattrs, or nonzero/incorrect exception handling around mover locks and disabled storage policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/sps/TestExternalStoragePolicySatisfier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitCache.java

## Purpose
`TestShortCircuitCache` verifies the DFSClient short-circuit read cache and its shared-memory coordination with DataNodes. It covers cache creation, invalid configurations, fetch-or-create reuse, expiry, eviction, time- and shared-memory-based staleness, shared-memory slot allocation/release, DataNode registry cleanup on failure, file descriptor request edge cases, domain socket closure across one or multiple DataNodes, and DataNode restart cleanup.

## Important APIs, Types, And Functions
The tests directly construct `ShortCircuitCache`, `ShortCircuitReplica`, `ShortCircuitReplicaInfo`, `ExtendedBlockId`, `DfsClientShmManager`, `DfsClientShm`, `ShortCircuitShm.Slot`, and `ShortCircuitRegistry`. `TestFileDescriptorPair` creates paired data and metadata files, including a `BlockMetadataHeader` with NULL checksum, and supplies `FileInputStream` pairs to cache replicas. `SimpleReplicaCreator` implements `ShortCircuitCache.ShortCircuitReplicaCreator` for deterministic cache insertions. Cluster tests use `MiniDFSCluster`, `DistributedFileSystem`, `BlockReaderFactory`, `BlockReaderTestUtil`, `DomainSocket`, `DomainPeer`, `TemporarySocketDirectory`, `PeerCache`, `DfsClientConf`, and Mockito fault injection.

The central cache APIs under test are `fetchOrCreate`, `unref`, `accept(CacheVisitor)`, `allocShmSlot`, `scheduleSlotReleaser`, `getDfsClientShmManager().visit`, and DataNode-side `ShortCircuitRegistry.registerSlot`/visitor queries. Failure-injector classes override `BlockReaderFactory.FailureInjector` hooks for request-file-descriptor failure and receipt-verification capability.

## Control Flow
Pure cache tests create local file descriptor pairs, call `fetchOrCreate` with block IDs, assert the same `ShortCircuitReplicaInfo` is reused while referenced or evictable, unref replicas, and then force expiry or eviction by time and capacity. Shared-memory tests create a short-circuit-enabled MiniDFSCluster with a domain socket path, use a domain peer to allocate slots, inspect the client-side shared-memory manager, and verify scheduled release eventually drains the segment and slot counts.

Failure and regression tests drive real short-circuit reads through `DFSTestUtil.readFileBuffer`, inject DataNode or BlockReaderFactory failures, and then assert the DataNode `ShortCircuitRegistry` has the expected segment/slot counts. Domain socket closure tests manually allocate/register slots and release them in different orders to make sure shutdown of one DataNode or one segment does not prematurely close unrelated shared memory. `testDNRestart` restarts the DataNode after slot allocation and ensures stale slots can be released without leaving registry or client manager state behind.

## State And Persistence Behavior
The key state is in-memory but backed by OS resources: file descriptors, domain sockets, memory-mapped/shared-memory segments, short-circuit replica reference counts, evictable maps, failed-load maps, and DataNode registry slot tables. Temporary data/meta files and temporary socket directories are local filesystem state cleaned by each test. MiniDFSCluster files provide real HDFS blocks whose local replicas are exposed through short-circuit reads. Tests explicitly check that invalidated slots are marked stale, registry counts fall to zero after release/failure, and cache eviction keeps only the newest eligible replicas.

## Dependencies And Integration Points
This suite integrates DFSClient short-circuit read code with DataNode xceiver behavior, domain sockets, shared memory, `BlockReaderFactory`, `PeerCache`, `ClientContext`, and DataNode-side `ShortCircuitRegistry`. It depends on native domain socket support and skips via `assumeTrue` when the domain socket library is unavailable. Mockito is used for `ClientContext`, `PeerCache`, `DomainSocket`, `ShortCircuitCache`, and `DataNodeFaultInjector` edge cases.

## Risks And Edge Cases
The tests guard against file descriptor leaks, stale shared-memory slots, incorrect retry behavior on `RetriableException`, NPEs when native file descriptor creation fails because of ulimit/native limitations, and cleanup failures when DataNode short-circuit shared-memory response fails. Timing sleeps and async `GenericTestUtils.waitFor` calls make some checks sensitive to scheduler delays. Some tests disable TCP reads for testing, so failure to perform short-circuit IO must surface as explicit non-TCP-read failures rather than silent fallback.

## Test Signals
Signals include exact cache reuse identity, creator callbacks being or not being invoked, visitor-observed segment/slot counts, valid/invalid slot flags, zero registry and manager counts after cleanup, expected exception text when forced short-circuit reads fail, and Mockito verification of retry/failure paths. Successful reads after clearing a failure injector confirm that the path map and registry recover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitLocalRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitLocalRead.java

## Purpose
`TestShortCircuitLocalRead` verifies local short-circuit HDFS block reads, including checksum and no-checksum modes, legacy block reader permissions/fallback, positional reads, direct `ByteBuffer` reads, skip/seek behavior, corrupt local block-file handling, remote block reader fallback behavior, and the deprecated `getBlockLocalPathInfo` permission gate. It also contains a standalone benchmark-oriented `main` method for comparing short-circuit and regular reads.

## Important APIs, Types, And Functions
The fixture uses `TemporarySocketDirectory` and `DomainSocket.disableBindPathValidation()` in `@BeforeAll`, with a per-test `assumeTrue` that native domain sockets loaded. `createFile` creates HDFS files using the configured block size. `checkFileContent` validates stream reads using `FSDataInputStream.readFully`, `IOUtils.skipFully`, small reads, chunk-boundary reads, and full reads. `checkFileContentDirect` repeats validation with `HdfsDataInputStream.read(ByteBuffer)` and a direct buffer. `doTestShortCircuitReadImpl` configures `HdfsClientConfigKeys.Read.ShortCircuit.KEY`, checksum skipping, random `DFS_CLIENT_CONTEXT`, domain socket path, optional legacy local-path user, and a one-DataNode MiniDFSCluster.

Other important APIs are `DFSUtilClient.createClientDatanodeProtocolProxy`, `ClientDatanodeProtocol.getBlockLocalPathInfo`, `DFSTestUtil.getFirstBlock`, `MiniDFSCluster.getBlockFile`, `RandomAccessFile.setLength`, `ClientContext.getDisableLegacyBlockReaderLocal`, `UserGroupInformation.doAs`, and `SubjectInheritingThread` for benchmark workers.

## Control Flow
The core test path creates deterministic random file content, writes it to a one-replica file, opens the cluster URI as a selected user, then checks both byte-array and direct-buffer read APIs from offset zero or a supplied offset. Small/long/read-offset tests vary file length and checksum skipping. Legacy tests supply `DFS_BLOCK_LOCAL_PATH_ACCESS_USER_KEY`; the fallback test reads as an unauthorized user and verifies legacy local reads become disabled after fallback.

The deprecated RPC test creates a block, obtains a block token and DataNode info, calls `getBlockLocalPathInfo` without configuring an allowed user, and expects an explanatory IOException. The skip test forces a short-circuit read before seeking across two blocks. The truncated block test writes two files, records the second file's content, truncates the first file's local block file to zero after cluster shutdown, restarts without formatting, verifies the corrupt file read fails, and then confirms the unrelated file still reads correctly. The remote block reader test enables short-circuit but omits a domain socket path, then confirms ordinary content reads still work and direct `ByteBuffer` read does not hit an unsupported-method failure.

## State And Persistence Behavior
Persistent state includes HDFS file contents, local DataNode block files, block tokens, client context flags, and optional legacy short-circuit disablement. The truncated-block test deliberately mutates the local block file on disk between cluster lifecycles to exercise corruption detection across restart. User identity state is simulated with `UserGroupInformation.createRemoteUser` and `doAs`; benchmark threads inherit subject state. Domain socket paths live in a temporary directory closed after all tests.

## Dependencies And Integration Points
The suite integrates DFSClient read paths, `BlockReaderLocal`, `HdfsDataInputStream`, legacy local block reader access control, DataNode local-path RPC, block-token security, domain sockets, and MiniDFSCluster local storage. It depends on `AppendTestUtil` for deterministic data, `TestBlockReaderLocal.assertArrayRegionsEqual` for byte comparison in one corruption path, and HDFS client configuration keys for short-circuit behavior.

## Risks And Edge Cases
Important edge cases are unauthorized legacy local reads falling back without data corruption, direct-buffer reads across chunk boundaries, offsets into small and multi-block files, skip with checksum verification enabled, distinguishing corrupt local data from communication failure, and ensuring one corrupt block file does not poison reads of another file. The benchmark `main` is not a JUnit test and assumes an external HDFS configuration, so it is more operational utility than CI signal.

## Test Signals
Signals are exact byte-for-byte comparisons against deterministic data, expected toggling of `ClientContext.getDisableLegacyBlockReaderLocal`, IOException text for unauthorized local-path RPC, failed reads from a zero-length block file, successful reads from the unaffected file after corruption, and command-return assertions in the remote-reader path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitLocalRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestAdminHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestAdminHelper.java

## Purpose
`TestAdminHelper` is a focused unit test for `AdminHelper.prettifyException`. It verifies how admin CLI helper code formats exceptions with and without explicit messages.

## Important APIs, Types, And Functions
The only production API under test is `AdminHelper.prettifyException(Throwable)`. The tests use JUnit 5 `@Test`, `assertTrue`, and `assertEquals`.

## Control Flow
`prettifyExceptionWithNpe` passes a plain `NullPointerException` and asserts the formatted string starts with the exception type plus the test method stack frame, proving message-less exceptions include useful location context. `prettifyException` passes an `IllegalArgumentException` with a cause and asserts only `IllegalArgumentException: Something is wrong` is emitted, proving the top-level message is preferred over nested-cause noise.

## State And Persistence Behavior
There is no persistent state. All behavior is pure string formatting of freshly constructed exceptions.

## Dependencies And Integration Points
This test supports HDFS admin tools that print user-facing exception summaries. It indirectly constrains CLI stderr/stdout quality because many admin commands call helper formatting when surfacing failures.

## Risks And Edge Cases
The NPE assertion includes a package and method prefix, so stack-frame naming changes or wrapper methods can break it. The cause-bearing exception test protects against overly verbose or misleading nested exception output.

## Test Signals
Signals are exact or prefix string matches. There is no MiniDFSCluster dependency, making this a fast unit-level guard for CLI error formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestAdminHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdmin.java

## Purpose
`TestDFSAdmin` is a broad JUnit 5 integration suite for the non-HA `DFSAdmin` CLI and helper methods. It validates DataNode information commands, block reports, volume reports, unreachable-DataNode failures, NameNode/DataNode reconfiguration, topology printing, cluster report corrupt-block accounting, open-file listing, snapshot/trash behavior, balancer bandwidth parsing, block-count reporting, proxy-user refresh, and multi-node reconfiguration fan-out for live and decommissioning DataNodes.

## Important APIs, Types, And Functions
The fixture creates a two-DataNode `MiniDFSCluster` in `setUp()`, with small block size, retry limits, trash interval, and snapshot trash root enabled. It owns `DFSAdmin`, current `DataNode`, current `NameNode`, captured `System.out`/`System.err`, and helper methods `redirectStream`, `resetStream`, `restartCluster`, `scanIntoList`, `scanIntoString`, `awaitReconfigurationFinished`, `waitForCorruptBlock`, `verifyOpenFilesListing`, `verifyNodesAndCorruptBlocks`, and `waitForReconfigurationDecommissionNode`.

Production APIs exercised include `ToolRunner.run(new DFSAdmin(conf), args)`, direct `DFSAdmin` methods for reconfiguration, `DFSClient` NameNode report methods, `DistributedFileSystem`, `FsShell`, `DFSTestUtil`, `BlockManagerTestUtil`, `DatanodeManager`, `DatanodeDescriptor`, `ReconfigurationUtil`, `DefaultImpersonationProvider`, and HDFS constants for reconfigurable properties and report arguments.

## Control Flow
Command tests redirect stdout/stderr, run `DFSAdmin` commands, scan output into lines, and assert exit codes plus content. Reconfiguration tests mock `ReconfigurationUtil.parseChangedProperties`, start reconfiguration on a node set, poll status until "finished", and inspect both output lines and actual in-process configuration/storage-location changes. Report tests build a separate cluster sized for an EC policy, create replicated and striped files, kill one DataNode, corrupt a replicated block and an EC block group, and assert `-report` output plus NameNode counters at each stage.

`testListOpenFiles` creates closed files and appended-open files, runs `-listOpenFiles` repeatedly while closing files one at a time, then tests path filtering, missing `-path` argument handling, empty-path behavior, and invalid-path behavior. Snapshot tests verify `.Trash` creation and permission semantics around `-allowSnapshot`/`-disallowSnapshot`. Proxy-user refresh first proves impersonation fails, writes a temporary config resource permitting proxying, runs `-refreshSuperUserGroupsConfiguration`, and then proves the proxy mkdir succeeds. Fan-out tests run reconfiguration over `livenodes` and mocked `decomnodes`.

## State And Persistence Behavior
State under test includes MiniDFSCluster DataNode/NameNode runtime state, DataNode volume directories, reconfiguration task state and output, block metadata and corruption counters, EC block group state, open lease state from unclosed append streams, snapshot-trash directories and permissions, cluster DataNode reports, and server-side proxy-user authorization configuration. Captured stdout/stderr are reset between command invocations. Temporary resources are deleted in `tearDown()`.

## Dependencies And Integration Points
This suite sits at the boundary between CLI parsing/output and HDFS server internals. It integrates `DFSAdmin` with DataNode IPC, NameNode RPC, block manager counters, EC policy support, trash/snapshot logic, `FsShell`, proxy user mappings, reconfiguration utilities, and block placement/reporting. It also uses Mockito to isolate reconfiguration deltas and decommissioning-node selection.

## Risks And Edge Cases
Output assertions depend on line counts, exact key names, and phrases, so legitimate CLI wording changes can require test updates. Corruption and open-file tests are asynchronous and rely on heartbeats, block reports, and polling. `testReportCommand` intentionally calls `tearDown()` and starts its own cluster, which is unusual and requires careful cleanup. The low-redundancy EC expected-string construction uses the replicated variable in one formatted string while comparing the EC counter separately, making output/counter coupling worth reviewing if report text changes. Reconfiguration over node groups must avoid duplicate or concurrent task races.

## Test Signals
Signals are command exit codes, stdout/stderr line content, exact counts of live/dead DataNodes, corrupt replicated blocks and EC block groups, highest-priority low-redundancy counters, open-file path presence/absence, real config value updates, storage directory formatting, `.Trash` permissions, and successful impersonation after refresh. Mockito call setup ensures reconfiguration tests are deterministic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdminWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdminWithHA.java

## Purpose
`TestDFSAdminWithHA` is a slow integration suite validating `DFSAdmin` behavior against an HA nameservice backed by a `MiniQJMHACluster`. It verifies that admin commands target both NameNodes where appropriate, handle partial and total NameNode outages, distinguish active-only commands from all-NameNode commands, and report correct stdout/stderr and exit codes for safemode, namespace save, restore failed storage, refresh commands, balancer bandwidth, metasave, finalize/upgrade, and open-file listing.

## Important APIs, Types, And Functions
`setUpHaCluster(boolean security)` creates `MiniQJMHACluster`, configures HA keys for nameservice `ns1` and NameNodes `nn1,nn2`, enables optional service authorization, redirects stdout/stderr, and lowers IPC/failover retry counts. `setHAConf` writes the HA nameservice/RPC address configuration. `assertOutputMatches` variants compare captured output and error against regexes and reset buffers. `tearDown` closes `DFSAdmin`, restores streams, and shuts down the cluster.

Production APIs under test include `DFSAdmin.run`, HA failover configuration, `MiniDFSCluster.transitionToActive`, NameNode shutdown/restart, `BootstrapStandby.run`, `HdfsServerConstants.StartupOption.UPGRADE`, and client retry/failover settings. The command surface includes `-safemode`, `-saveNamespace`, `-restoreFailedStorage`, `-refreshNodes`, `-setBalancerBandwidth`, `-metasave`, `-refreshServiceAcl`, `-refreshUserToGroupsMappings`, `-refreshSuperUserGroupsConfiguration`, `-refreshCallQueue`, `-finalizeUpgrade`, `-upgrade query/finalize`, and `-listOpenFiles`.

## Control Flow
Each test creates a fresh HA cluster, optionally transitions one NameNode active or shuts one/both NameNodes down, runs a `DFSAdmin` command, then validates exit code and output regex. Commands that operate on all NameNodes, such as safemode and refresh operations, are expected to print one line per NameNode when both are up and to return nonzero with mixed stdout/stderr when one NameNode is down. Active-only commands such as balancer bandwidth and metasave require an active NameNode and have special standby-skip or all-down failure behavior. Upgrade tests explicitly shut down both NameNodes, restart one with `-upgrade`, bootstrap the standby, query not-finalized/finalized states, and finalize through DFSAdmin.

## State And Persistence Behavior
State includes HA nameservice configuration, QJM-backed NameNode metadata, active/standby role state, safemode state, restore-failed-storage flag, upgrade/finalization state, service authorization setting, captured stdout/stderr, and the availability of each NameNode process. Startup option changes on NameNode info persist across restart for the upgrade scenario. Output buffers are cleared after every assertion to isolate command effects.

## Dependencies And Integration Points
The suite integrates `DFSAdmin` with HA proxy/failover resolution, quorum journal MiniCluster, NameNode lifecycle control, bootstrap standby tooling, service authorization refresh, and HDFS client failover retry policies. It complements `TestDFSAdmin` by focusing on HA fan-out and partial-failure semantics rather than DataNode and block-manager details.

## Risks And Edge Cases
Regex-based output checks are sensitive to wording and line-separator handling. Partial-outage scenarios must return nonzero for commands that failed on one peer while still preserving successful output from the available peer. Commands that should route only to active NameNodes must not be broken by standby peers. The upgrade test is stateful and long-running because it manipulates startup options and standby bootstrap; cleanup must restore streams and shut down all processes.

## Test Signals
Signals are exit codes, one-line-per-NameNode output patterns, mixed stdout/stderr on partial failures, "2 exceptions" messages when both NameNodes are down, active-only success for balancer bandwidth/list-open-files, standby skip for metasave, and upgrade query/finalize messages before and after startup-option transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSAdminWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdmin.java

## Purpose
`TestDFSHAAdmin` is a Mockito-based unit/integration-style test for the `DFSHAAdmin` HA management CLI. It verifies nameservice option parsing, NameNode target resolution, help text, all-service-state listing, manual state transitions, automatic-HA restrictions, monitoring operations, failover and fencing options, health checks, service-state reporting, graceful failover through ZKFC, and per-nameservice/per-NameNode fencing configuration precedence.

## Important APIs, Types, And Functions
The fixture builds an HA `HdfsConfiguration` for nameservice `ns1` with `nn1` and `nn2` RPC addresses. In `setup()`, `DFSHAAdmin` is subclassed so `resolveTarget` returns a spy `HAServiceTarget` whose `getProxy` returns a mocked `HAServiceProtocol` and whose `getZKFCProxy` returns a mocked `ZKFCProtocol`. Captured output streams are wired through `tool.setErrOut` and `tool.setOut`.

Key HA APIs under test are `HAServiceProtocol.transitionToActive`, `transitionToStandby`, `transitionToObserver`, `getServiceStatus`, `monitorHealth`, `HAServiceStatus`, `StateChangeRequestInfo`, `RequestSource`, and `ZKFCProtocol.gracefulFailover`. Fencing paths use shell fencer commands selected by `getFencerTrueCommand`/`getFencerFalseCommand` for Unix versus Windows. `runTool` resets buffers, calls `tool.run(args)`, records output strings, and returns the CLI status.

## Control Flow
Parsing tests run `-ns` combinations and `-help`, checking missing nameservice/command errors and lazy validation. Resolution tests run `-getServiceState` for a known and unknown NameNode. Transition tests mock a standby-ready status, run transition commands, and capture `StateChangeRequestInfo` to verify request source. When automatic HA is enabled, mutative transition commands fail unless `-forcemanual` is supplied; the forced path injects `yes` into `System.in` and expects `REQUEST_BY_USER_FORCED`.

Failover tests vary fencer configuration, `--forcefence`, `--forceactive`, bad arguments, option ordering, and auto-HA. With auto-HA enabled, `-failover` is expected to call `ZKFCProtocol.gracefulFailover` rather than manual protocol transitions. Health tests check success and a mocked `HealthCheckFailedException`. Fencing precedence tests first use the default fencer, then override with NameNode-specific and nameservice-specific keys to verify failure/success precedence.

## State And Persistence Behavior
No real HDFS cluster or persistent metadata is created. State is test-local configuration, mocked protocol behavior, captured stdout/stderr, Mockito invocation history, and temporary `System.in` replacement for manual confirmation. The CLI output strings are refreshed on every `runTool` call.

## Dependencies And Integration Points
This test targets DFSHAAdmin's integration with Hadoop HA abstractions rather than MiniDFSCluster. It depends on `DFSUtil` key suffix generation, `HAServiceTarget` resolution from HDFS configuration, `HAServiceProtocol`, `ZKFCProtocol`, fencer configuration keys, shell fencing command syntax, and Mockito protocol mocks. It complements `TestDFSAdminWithHA` by testing fine-grained command parsing and protocol calls without a real HA cluster.

## Risks And Edge Cases
Important edge cases are refusing manual mutative operations under auto-failover, preserving monitoring operations under auto-failover, prompting and forced request-source semantics for `-forcemanual`, invalid fencer/force arguments, nameservice option placement, target-resolution error messages, and platform-specific fencer commands. Tests that replace `System.in` can leak input state if expanded without cleanup.

## Test Signals
Signals are CLI return codes, output substrings, Mockito verification of protocol method calls, captured `StateChangeRequestInfo` sources, absence of mutative calls when auto-HA blocks them, invocation of `gracefulFailover` for auto-HA failover, and pass/fail outcomes under default, nameservice-specific, and NameNode-specific fencer keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSHAAdmin.java -->
