# subset-b-007557 research

This grouped report covers HDFS NameNode HA tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha`. Each section is source-path aligned and wrapped for reconciliation into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencing.java

## Purpose
`TestDNFencing` is a regression and integration suite for DataNode fencing during HDFS HA failover. It verifies that queued block invalidations, block reports, append-related replica states, and standby `PendingDataNodeMessages` do not cause data loss or corrupt replicas when a standby becomes active while the former active still has deletion commands in flight.

## Important APIs, Types, And Functions
The fixture builds a two-NameNode, three-DataNode `MiniDFSCluster` using `MiniDFSNNTopology.simpleHATopology()`, small block size, long redundancy interval, high replication streams, a short edit-tailing period, and a custom `RandomDeleterPolicy`. Core tests are `testDnFencing`, `testNNClearsCommandsOnFailoverAfterStartup`, `testNNClearsCommandsOnFailoverWithReplChanges`, `testBlockReportsWhileFileBeingWritten`, `testQueueingWithAppend`, and `testRBWReportArrivesAfterEdits`. Helpers include `doMetasave`, `waitForTrueReplication`, `getTrueReplication`, and the nested `RandomDeleterPolicy`.

## Control Flow
Most tests create or append files, force replication changes or block reports, deliberately leave `nn1` believing it is active by aborting edit logs and entering safe mode, then transition `nn2` to active. They trigger heartbeats, full block reports, deletion reports, redundancy rescans, and postponed-misreplicated-block rescans before asserting that the new active converges to safe metadata. Append tests exercise RBW, FINALIZED, OP_ADD, OP_UPDATE_BLOCKS, and OP_CLOSE ordering across failover. `testRBWReportArrivesAfterEdits` delays a DataNode block report to the standby with a Mockito `DelayAnswer`.

## State And Persistence
Persistent state under test is HDFS namespace edits and block replica metadata. The suite stresses transient NameNode state: invalidation queues, pending reconstruction, pending DataNode messages, postponed misreplicated blocks, corrupt replica accounting, and actual DataNode on-disk replica files. `RandomDeleterPolicy` randomizes excess-replica deletion to force the two NameNodes to choose different replicas, amplifying fencing bugs.

## Dependencies And Integration Points
The tests integrate `MiniDFSCluster`, `HATestUtil`, `NameNodeAdapter`, `BlockManagerTestUtil`, `DataNodeTestUtils`, `InternalDataNodeTestUtils`, `AppendTestUtil`, `DFSTestUtil`, `DatanodeProtocolClientSideTranslatorPB`, and Mockito. They validate coordination among HA state transitions, edit log tailing, DataNode heartbeats/block reports, block manager invalidation, and client failover filesystems.

## Risks
The risky behavior is split-brain-like command delivery: a DataNode may hold deletion commands from the old active while the new active needs a different replica set. Regressions can appear as under-replication, pending replication that never drains, corrupt replicas after RBW reports are replayed too late, or non-readable files even though namespace edits appear correct. Tests are timing-sensitive because they rely on reports, heartbeats, delayed RPCs, and redundancy monitor work.

## Test Signals
Success is signaled by zero postponed misreplicated blocks, zero under-replicated and pending-replication counts, zero corrupt replica blocks, successful `DFSTestUtil.readFile` or `AppendTestUtil.check`, and a true physical replica count after DataNode deletions. The metasave logging is diagnostic only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencingWithReplication.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencingWithReplication.java

## Purpose
`TestDNFencingWithReplication` is a slow stress test for HA fencing while replication levels are repeatedly changed during failovers. It targets races between block reconstruction, deletion, block reports, failover proxy retries, and active NameNode changes.

## Important APIs, Types, And Functions
The main test is `testFencingStress`. It uses `HAStressTestHarness` with three NameNodes, one active at a time, short block report and redundancy intervals, and a failover filesystem. The nested `ReplicationToggler` extends `RepeatingTestThread` and alternates a file between replication factor 1 and 2, using `waitForReplicas` to poll block locations until the observed host count matches the requested factor.

## Control Flow
The test creates 20 files at replication 3, starts one toggler per file, adds a harness thread that frequently triggers deletion reports and replication work, and adds a failover thread that changes the active NameNode every five seconds. After the runtime window, it stops all threads and reads every file back through the HA filesystem.

## State And Persistence
The persistent state is the contents and replication metadata of the 20 HDFS files. Transient state includes concurrent client replication changes, NameNode block manager work queues, DataNode block/deletion reports, retry invocation state, and changing active/standby roles across three NameNodes.

## Dependencies And Integration Points
This file integrates `HAStressTestHarness`, `MiniDFSCluster`, `DFSTestUtil`, `FileSystem.setReplication`, `getFileBlockLocations`, `BlockLocation`, `GenericTestUtils.waitFor`, and `MultithreadedTestUtil`. It also suppresses noisy FSNamesystem audit, server, and retry logs for stress execution.

## Risks
The test is intentionally nondeterministic and long-running. Failures may reflect true fencing races, slow replication under local load, or timeouts waiting for block locations. Any change to block placement, redundancy scheduling, heartbeat timing, or failover retry behavior can affect it.

## Test Signals
The primary signals are successful toggler execution without uncaught exceptions, `waitForReplicas` reaching both target replica counts, and every file remaining readable after repeated failovers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencingWithReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDelegationTokensWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDelegationTokensWithHA.java

## Purpose
`TestDelegationTokensWithHA` validates delegation token issuance, renewal, cancellation, logical service names, token cloning, and observer-read behavior in an HA cluster. It covers both client-facing DFS APIs and low-level NameNode token verification during failover.

## Important APIs, Types, And Functions
The fixture enables `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, configures auth-to-local rules, creates a two-NameNode HA cluster with no DataNodes, sets failover configurations, and captures `DelegationTokenSecretManager` from the active. Tests include `testObserverReadProxyProviderWithDT`, `testDelegationTokenDFSApi`, `testDelegationTokenDuringNNFailover`, `testDelegationTokenWithDoAs`, `testHAUtilClonesDelegationTokens`, `testDFSGetCanonicalServiceName`, `testHdfsGetCanonicalServiceName`, and `testCancelAndUpdateDelegationTokens`. Helpers include `getDelegationToken`, `doRenewOrCancel`, `TokenTestAction`, and a blocking `EditLogTailerForTest`.

## Control Flow
The DFS API test gets a token from the HA filesystem, decodes the identifier, verifies the password in the active secret manager, renews through both direct manager and client configuration, checks a bad configuration error, fails over to the second NameNode, then renews and cancels again. The failover-transition test stops the standby tailer, installs a tailer that waits on a monitor, creates a token, transitions the old active to standby, starts transition of the other NameNode to active in another thread, expects standby or retriable exceptions during the transition, then releases tailing and verifies renewal/cancel. Observer-read with delegation tokens recreates a filesystem under a UGI carrying the token and verifies standby/probe failure logging and routing.

## State And Persistence
Token state is stored in NameNode delegation token secret managers and replicated through edit logs. The tests observe token identifiers, passwords, services, UGI token collections, canonical service names, and the edit-log tailer's catch-up gate. `SecurityUtilTestHelper.setTokenServiceUseIp` switches service identity semantics between IP-based and host-based token services.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `HATestUtil`, `HAUtilClient`, `DelegationTokenIdentifier`, `DelegationTokenSelector`, `UserGroupInformation`, `SecurityUtil`, `SubjectInheritingThread`, `ObserverReadProxyProvider`, `AbstractFileSystem`, `DistributedFileSystem`, and `Whitebox`. The tests connect security token code to HA logical URIs, physical NameNode addresses, failover proxy providers, observer reads, and edit log tailing.

## Risks
Failures here can break secure HA clients even if unsecured HA works. Risk centers on token service names for logical URIs, stale secret-manager state during failover, incorrect exception types while transitioning, UGI token replacement after cancellation, and observer read probes that authenticate with delegation tokens. The test uses shared static configuration and mutates security helper state, so cleanup ordering matters.

## Test Signals
Signals include successful token password retrieval, renew/cancel calls before and after failover, expected IOException text for missing logical nameservice mapping, expected `StandbyException` or `RetriableException` during transition, correct UGI token counts and cloned physical-token selection, correct canonical service names, and successful filesystem access after token update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDelegationTokensWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogTailer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogTailer.java

## Purpose
`TestEditLogTailer` validates standby edit log tailing, log roll triggering, backoff, in-progress edit tailing, active roll timeouts, retry behavior across multiple remote NameNodes, and thread interruption handling. It is parameterized for synchronous and asynchronous edit logging modes.

## Important APIs, Types, And Functions
The class is a JUnit parameterized class over `useAsyncEditLog`. Key tests are `testTailer`, `testTailerBackoff`, `testNN0TriggersLogRolls`, `testNN1TriggersLogRolls`, `testNN2TriggersLogRolls`, `testTriggersLogRollsForAllStandbyNN`, `testRollEditTimeoutForActiveNN`, `testRollEditLogIOExceptionForRemoteNN`, `testStandbyTriggersLogRollsWhenTailInProgressEdits`, and `testRollEditLogHandleThreadInterruption`. Helpers include `getConf`, `testStandbyTriggersLogRolls`, `waitForLogRollInSharedDir`, `waitForStandbyToCatchUpWithInProgressEdits`, `checkForLogRoll`, and `createMiniDFSCluster`.

## Control Flow
`testTailer` writes directories on the active, waits for standby catch-up, compares last-written and last-applied transaction IDs, and reads the directories from the standby. Backoff testing uses mocked `FSNamesystem`, `FSImage`, and `NNStorage` plus a custom `EditLogTailer` that records sleep durations as consecutive zero-edit polls grow from 2 to 10 ms and reset to 1 ms after edits appear. Log-roll tests start three NameNodes with fixed IPC ports, move one active, and wait for shared edits files to roll. Timeout and IO tests spy on the tailer's `getNameNodeProxy` to simulate slow, failing, or interrupted remote roll calls.

## State And Persistence
The test observes namespace edits, shared edit-log segment files, current segment transaction IDs, `lastAppliedTxId`, `lastRollTimeMs`, and in-progress/finalized edits files under the shared edits directory. It also manipulates the tailer's timer with `FakeTimer` to prove that tailing in-progress edits does not trigger premature rolls.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `EditLogTailer`, `FSEditLog`, `FSImage`, `NNStorage`, `NameNodeAdapter`, `HAUtil`, Mockito, `GenericTestUtils`, and `FakeTimer`. The tests exercise tailer interaction with shared edits storage, active NameNode RPC rollEditLog, multiple NameNode proxy selection, and in-progress edit tailing configuration.

## Risks
Timing and port allocation are the main risks. Bind conflicts are retried in one path, and several assertions depend on log files appearing within fixed windows. Changes to transaction ID semantics, async edit logging, proxy retry counts, or active roll timeout behavior can break these tests.

## Test Signals
Signals include directories visible on the standby, matching transaction accounting, exact backoff durations `[2, 4, 8, 10, 10, 1]`, existence of expected in-progress or finalized edits files, timeout behavior without completing slow roll calls, expected retry invocation counts, and `lastRollTimeMs` advancing only after a successful remote roll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogTailer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogsDuringFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogsDuringFailover.java

## Purpose
`TestEditLogsDuringFailover` checks edit-log file handling when HA NameNodes start, restart, and fail over. It verifies that standbys do not consume in-progress logs at startup, and that a NameNode transitioning to active finalizes and reads abandoned in-progress shared edits safely.

## Important APIs, Types, And Functions
The tests use `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HAUtil.setAllowStandbyReads`, `NNStorage` edit-file naming helpers, `FSImageTestUtil.createAbortedLogWithMkdirs`, and `NameNodeAdapter.getFileInfo`. Important methods are `testStartup`, `testFailoverFinalizesAndReadsInProgressSimple`, `testFailoverFinalizesAndReadsInProgressWithPartialTxAtEnd`, `testFailoverFinalizesAndReadsInProgress`, `assertNoEditFiles`, and `assertEditFiles`.

## Control Flow
`testStartup` starts both NameNodes in standby and asserts that local and shared edit directories contain no edit files. It transitions NN0 active, verifies that only NN0 local dirs and shared edits get an in-progress segment, writes `/test`, restarts the standby, and asserts the standby neither finalized shared edits nor applied the in-progress segment. After another mkdir and NN0 restart, it transitions NN1 active and checks both edits are visible. The failover helper creates a fake aborted in-progress shared log, optionally appends a partial transaction, transitions a NameNode active, and verifies it can read the complete mkdir operations, ignore the partial tail, finalize the old segment, and open a new segment.

## State And Persistence
The file directly inspects NameNode storage directories and shared edits files. Persistent state includes generated `edits_inprogress_*` and finalized `edits_*` files plus mkdir transactions. It globally disables edit-log fsync for test speed.

## Dependencies And Integration Points
This test integrates NameNode storage layout, shared edits storage, FSImage test utilities, failover activation, and RPC namespace operations. It also uses `GenericTestUtils.assertGlobEquals` to enforce exact directory contents.

## Risks
Incorrect handling can double-replay edits, start replay in the middle of a segment, finalize a segment while a standby is merely starting, or fail activation when a partial transaction exists at the end of an abandoned log. Because it inspects filenames, changes to edit-log naming or txid numbering require coordinated test updates.

## Test Signals
Success is exact edit-file presence or absence, null/non-null file info checks for `/test` and `/test2`, successful activation after reading fake logs, and expected finalized plus next in-progress segment names in the shared edits directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogsDuringFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailoverWithBlockTokensEnabled.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailoverWithBlockTokensEnabled.java

## Purpose
`TestFailoverWithBlockTokensEnabled` verifies that HA clusters with HDFS block access tokens enabled keep token serial numbers distinct, reject tampered block tokens, and continue reading/writing after failover and block-token key updates.

## Important APIs, Types, And Functions
The fixture enables `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, reduces retry window base, and starts a three-NameNode HA topology with one DataNode. Tests are `ensureSerialNumbersNeverOverlap`, `ensureInvalidBlockTokensAreRejected`, `testFailoverAfterRegistration`, and `TestFailoverAfterAccessKeyUpdate`. Helpers include `setAndCheckSerialNumber`, `writeUsingBothNameNodes`, `lowerKeyUpdateIntervalAndClearKeys`, and its namesystem overload.

## Control Flow
The serial test sets the same nominal serial number on all NameNode `BlockTokenSecretManager` instances and verifies each manager maps it to a unique effective serial. The invalid-token test writes a file, spies the `DFSClient`, alters each returned block token identifier expiry while keeping the old password, installs the spy back into the `DistributedFileSystem`, and expects read failure. Failover tests write on NN0 active, transition NN0 standby and NN1 active, delete and rewrite the file, optionally after lowering token key intervals and clearing NameNode/DataNode keys.

## State And Persistence
Persistent state is one HDFS file at `/test-path`; security state includes block token secret manager keys, serial numbers, token lifetime/update interval, DataNode cached block secret keys, and located block tokens returned to clients. Tampered token state is injected only in the client-side located-block response path.

## Dependencies And Integration Points
Dependencies include `BlockTokenSecretManager`, `BlockTokenIdentifier`, `DFSClientAdapter`, `LocatedBlocks`, `LocatedBlock`, `DataNode`, `FSNamesystem`, Mockito, `DFSTestUtil`, and `HATestUtil`. The tests connect HA failover, DataNode registration/key propagation, client block reads, and token validation.

## Risks
Block-token serial overlap across NameNodes can let one NameNode validate another's stale keys incorrectly. Short key intervals and sleeps are timing-sensitive. The invalid token path depends on token password mismatch behavior and exact client error text.

## Test Signals
Signals include non-equal effective serial numbers for all manager pairs, expected `Could not obtain block` failure for tampered tokens, and successful write/delete/write operations on different active NameNodes before and after key updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailoverWithBlockTokensEnabled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureOfSharedDir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureOfSharedDir.java

## Purpose
`TestFailureOfSharedDir` verifies configuration and runtime behavior for HA shared edits directories. It ensures the shared edits dir is treated as required, multiple shared dirs are rejected, shared dirs are ordered before local edits dirs, and runtime failure of the required shared dir prevents unsafe log rolling.

## Important APIs, Types, And Functions
Tests are `testSharedDirIsAutomaticallyMarkedRequired`, `testMultipleSharedDirsFails`, `testSharedDirsComeFirstInEditsList`, and `testFailureOfSharedDir`. They use `FSNamesystem.getRequiredNamespaceEditsDirs`, `FSNamesystem.getNamespaceEditsDirs`, `DFS_NAMENODE_SHARED_EDITS_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`, `MiniDFSCluster`, `NNStorage`, and `FileUtil.chmod`.

## Control Flow
The configuration tests create synthetic URI lists and assert required-dir inclusion, rejection of comma-separated shared edits dirs, and ordering of shared then local dirs. The runtime test starts an HA cluster with exit-on-shutdown disabled, makes NN0 active, writes a directory, removes write permission from the shared edits dir, waits for resource checking, verifies the standby remains standby and not in safe mode, then tries `rollEditLog` on the active and expects an `ExitException`.

## State And Persistence
Persistent state includes local and shared NameNode edit directories and their edit-log files. The runtime test mutates filesystem permissions on the shared edits directory and later restores them for cleanup. It inspects local edits dirs to verify they did not roll independently after shared-dir finalization failed.

## Dependencies And Integration Points
This file integrates configuration parsing in `FSNamesystem`, resource checking, NameNode RPC log rolling, shared edit journal ordering, `MiniDFSCluster` shutdown behavior, and `GenericTestUtils.assertGlobEquals`.

## Risks
If shared edits are not required or not synced first, local journals can advance beyond shared journals and break standby catch-up. Runtime permission mutation can affect cleanup if not restored. Assertions depend on exact exception text and edit-file names.

## Test Signals
Signals include expected URI membership/order, exact IOException message for multiple shared dirs, standby remaining out of safe mode during resource unavailability, expected `finalize log segment 1, 3 failed for required journal` exit text, and local edits dirs still containing only `edits_inprogress_0000000000000000001`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureOfSharedDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureToReadEdits.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureToReadEdits.java

## Purpose
`TestFailureToReadEdits` injects edit-log read failures into standby NameNodes to verify they do not double-replay earlier edits, can checkpoint consistently after partial progress, and refuse to become active if all available edits cannot be read.

## Important APIs, Types, And Functions
The class is parameterized over `TestType.SHARED_DIR_HA` and `TestType.QJM_HA`, with async edit logging currently disabled in the data set. Tests are `testFailuretoReadEdits`, `testCheckpointStartingMidEditsFile`, and `testFailureToReadEditsOnTransitionToActive`. Helpers include `setUpCluster`, `tearDownCluster`, `causeFailureOnEditLogRead`, and nested `LimitedEditLogAnswer`, which wraps selected `EditLogInputStream` instances and throws when reading the mkdir op for `/test3`.

## Control Flow
Setup builds either file-based shared-dir HA or QJM HA with aggressive checkpoint settings and standby reads enabled, transitions NN0 active, and creates an HA filesystem. The main replay test creates `/test1`, catches up standby, performs owner change and delete, creates `/test2` and `/test3`, then causes standby tailing to fail on the `/test3` edit. It verifies `/test1` is deleted, `/test2` exists, `/test3` does not, then disables failure and verifies full catch-up. Checkpoint testing allows the standby to checkpoint after partial edit application and verifies both active and standby can restart and eventually see all directories. Transition testing shuts down the active and expects standby activation to fail with edit replay error.

## State And Persistence
State includes active and standby namespace trees, edit-log stream position, checkpoints retained on both NameNodes, and QJM or shared-dir journal data. The injected failure is transient Mockito state on the standby edit log selection/read path.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniQJMHACluster`, `FSEditLog`, `EditLogInputStream`, `FSEditLogOp`, `NameNodeAdapterMockitoUtil`, `NameNodeAdapter`, `HATestUtil`, `DFSUtilClient`, and `GenericTestUtils`. The test connects journal implementations, checkpointing, edit tailing, and transition-to-active safety.

## Risks
The critical risk is partial replay corrupting namespace state or producing checkpoints at non-segment boundaries that active NameNodes cannot consume. The Mockito hook depends on `NameNodeAdapter.getMkdirOpPath(op)` recognizing the target operation. QJM and shared-dir behavior must remain equivalent.

## Test Signals
Signals include `CouldNotCatchUpException` while failure is active, exact namespace visibility on standby before and after removing the failure, checkpoints at expected txids, successful active restart and file existence checks, and `ExitException` containing `Error replaying edit log` when activation is unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureToReadEdits.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestGetGroupsWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestGetGroupsWithHA.java

## Purpose
`TestGetGroupsWithHA` adapts the generic `GetGroupsTestBase` to an HA HDFS cluster, ensuring the `GetGroups` admin tool resolves and contacts NameNodes correctly through HA failover configuration.

## Important APIs, Types, And Functions
The class extends `GetGroupsTestBase`, overrides `getTool(PrintStream)` to return `new GetGroups(conf, o)`, and uses JUnit `setUpNameNode`/`tearDownNameNode` to manage a no-DataNode `MiniDFSCluster` with `MiniDFSNNTopology.simpleHATopology()`.

## Control Flow
Setup creates a fresh `HdfsConfiguration`, starts the HA cluster, and calls `HATestUtil.setFailoverConfigurations` so the inherited base tests run the tool against a logical nameservice rather than a single physical NameNode. Teardown shuts down the cluster.

## State And Persistence
There is no meaningful persistent HDFS data. Test state is the HA cluster configuration and the base class's group-mapping assertions/output capture.

## Dependencies And Integration Points
The test integrates `GetGroups`, `GetGroupsTestBase`, `MiniDFSCluster`, `MiniDFSNNTopology`, and `HATestUtil`. It covers the non-`ClientProtocol` group-mapping RPC path in an HA configuration.

## Risks
Failures point to HA logical URI/proxy configuration issues for tools outside normal filesystem operations. Because the actual assertions live in the base class, this class is mostly wiring and can miss HA transition scenarios.

## Test Signals
Inherited `GetGroupsTestBase` tests pass using the HA-configured `GetGroups` tool, and teardown completes without cluster leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestGetGroupsWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAAppend.java

## Purpose
`TestHAAppend` is a focused regression test for append and truncate edit processing during HA catch-up and failover. It targets a case where pending DataNode messages plus split edit-log segments could incorrectly mark a block corrupt.

## Important APIs, Types, And Functions
The file defines `COUNT = 5`, helper `createAndHflush`, and one test, `testMultipleAppendsDuringCatchupTailing`. It uses `AppendTestUtil`, `MiniDFSCluster`, `MiniDFSNNTopology`, `HATestUtil`, `DFSck`, `ToolRunner`, and `TestFileTruncate.checkBlockRecovery`.

## Control Flow
The test disables automatic log rolling, lengthens edit tailing, creates one append target and one truncate target, writes initial data with `hflush`, rolls edits and manually tails them into the standby, then closes streams. It performs several append-close cycles, truncates the second file, triggers block reports so the standby sees block reports before edits, shuts down NN0, and transitions NN1 active. It runs `DFSck`, checks corrupt block count, verifies the appended file's full contents, and verifies truncation content after optional block recovery.

## State And Persistence
Persistent state consists of two files, their block metadata, append OP_ADD/OP_UPDATE_BLOCKS/OP_CLOSE edits, and truncate edits. Transient state includes pending DataNode message queues and the standby's delayed edit tailing.

## Dependencies And Integration Points
This test integrates client append/truncate APIs, manual edit-log roll/tail control, failover activation, DataNode block reports, fsck, and block recovery. It is directly tied to HDFS-3605 behavior.

## Risks
Ordering is the main risk: block reports can arrive ahead of corresponding edits, and append close edits can cross log-segment boundaries. Random file partitions make coverage less fixed but still deterministic enough for content verification.

## Test Signals
Signals include `DFSck` returning 0, zero corrupt replica blocks on the new active, `AppendTestUtil.checkFullFile` for appended and truncated files, and successful block recovery when truncate is not immediately ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAConfiguration.java

## Purpose
`TestHAConfiguration` is a daemon-light unit test suite for HA configuration validation and interpretation. It checks checkpointer setup, peer NameNode address discovery, duplicate edit-dir removal, SecondaryNameNode rejection in HA, and generic configuration generation for other HA nodes.

## Important APIs, Types, And Functions
The class uses a mocked `FSNamesystem`, helper `getHAConf`, and tests `testCheckpointerValidityChecks`, `testGetOtherNNHttpAddress`, `testHAUniqueEditDirs`, `testSecondaryNameNodeDoesNotStart`, and `testGetOtherNNGenericConf`. It exercises `StandbyCheckpointer`, `NameNode.initializeGenericKeys`, `FSNamesystem.getNamespaceEditsDirs`, `SecondaryNameNode`, `HAUtil.getConfForOtherNodes`, and `DFSUtil.addKeySuffixes`.

## Control Flow
Tests synthesize HA configurations with nameservices, NameNode IDs, RPC/service RPC addresses, and edits dirs. They instantiate configuration consumers and assert derived values or expected exceptions. HTTP address discovery verifies that missing HTTP host defaults are substituted from RPC addresses, including the three-NameNode case.

## State And Persistence
There is no persistent cluster state. The state under test is configuration key/value data, derived generic keys, lists of remote NN URLs, and parsed URI collections.

## Dependencies And Integration Points
The file integrates HDFS configuration constants, `DFSUtil`, `HAUtil`, `StandbyCheckpointer`, `FSNamesystem`, `NameNode`, and `SecondaryNameNode`. It protects admin-facing configuration behavior without starting full clusters.

## Risks
Subtle configuration changes can break checkpoint upload targets, accidentally allow SecondaryNameNode in HA, or choose wrong peer addresses. Tests rely on non-local IPs to avoid local address matching and exact error-message fragments.

## Test Signals
Signals include expected `IllegalArgumentException` for invalid checkpointer config, correct peer HTTP URLs, duplicate edit-dir count of two, expected SecondaryNameNode IOException, and generated peer configuration with `nn2` identity and no stale service RPC generic key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAFsck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAFsck.java

## Purpose
`TestHAFsck` verifies that the `DFSck` command works against an HA nameservice before and after failover, and when one standby NameNode is stopped. It runs the same scenario for configured failover and request-hedging proxy providers.

## Important APIs, Types, And Functions
The parameterized class takes a proxy-provider class name from `data`: `ConfiguredFailoverProxyProvider` or `RequestHedgingProxyProvider`. The main test is `testHaFsck`, with helper `runFsck`. It uses a `MiniDFSNNTopology` with explicit HTTP ports, `HATestUtil.setFailoverConfigurations`, `FileSystem`, `DFSck`, and `ToolRunner`.

## Control Flow
The test starts a two-NameNode cluster, transitions NN0 active, configures HA failover, creates `/test1` and `/test2`, and runs fsck. It then fails over to NN1 and runs fsck again. Finally it stops the old standby and runs fsck a third time, proving the command can still find the active.

## State And Persistence
The persistent namespace state is two test directories. Runtime state includes active/standby roles, HTTP endpoint configuration, and the selected client proxy provider.

## Dependencies And Integration Points
This test covers integration among `DFSck`, HA logical URI configuration, NameNode HTTP ports, client failover providers, and active NameNode discovery.

## Risks
Fsck uses both RPC and HTTP-oriented NameNode information, so HA configuration bugs can surface differently than normal `FileSystem` calls. Request hedging can mask or expose standby failures depending on provider behavior.

## Test Signals
`runFsck` expects exit code 0 and output containing both `/test1` and `/test2` in all three phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAFsck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAMetrics.java

## Purpose
`TestHAMetrics` verifies HA-related NameNode metrics and state reporting: HA state names, millis since last loaded edits, pending DataNode message count, inode count after restart from fsimage, and ordinal `getNameNodeState()` values including observer and initializing states.

## Important APIs, Types, And Functions
Tests are `testHAMetrics`, `testHAInodeCount`, and `testGetNameNodeState`. They use `FSNamesystem.getHAState`, `getMillisSinceLastLoadedEdits`, `getPendingDataNodeMessageCount`, `getFilesTotal`, NameNode MXBean attribute `LastHATransitionTime`, `NameNode.getNameNodeState`, `MiniDFSCluster`, `DistributedFileSystem.saveNamespace`, and safe mode actions.

## Control Flow
The metrics test starts two NameNodes, checks initial standby metrics, transitions NN0 active and reads the JMX transition time, flips active to NN1, waits for standby lag, creates a file so the standby accumulates pending DataNode messages, then waits for catch-up and verifies the counters drop and loaded-edits age decreases. The inode test creates four files, saves namespace, flips active, restarts the former active as standby, and checks its file count from loaded image. The state API test starts three NameNodes, transitions active and observer states, then shuts one down and expects INITIALIZING.

## State And Persistence
State includes JMX NameNodeStatus metrics, in-memory FSNamesystem counters, pending DN message queues, fsimage contents, and HA service state. Persistent namespace state is created files and saved fsimage.

## Dependencies And Integration Points
The tests integrate metrics exposure, JMX, safe mode namespace saving, edit tailing, pending DataNode message draining, observer state transitions, and cluster restart/shutdown behavior.

## Risks
Metrics can be racy because they are time-based and depend on tailing cadence. `LastHATransitionTime` assumes monotonic increase across transitions. Inode count after restart protects against stale metrics when loading from fsimage rather than replaying edits.

## Test Signals
Signals include exact HA state strings, positive or zero millis-since-edits according to active/standby role, increasing JMX transition time, pending message count changing from positive to zero after catch-up, file total count of five after restart, and ordinal service-state matches for STANDBY, ACTIVE, OBSERVER, and INITIALIZING.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHASafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHASafeMode.java

## Purpose
`TestHASafeMode` is a broad slow suite for safe mode behavior in HA clusters. It validates client retry while active is in safe mode, standby safe-block accounting while edits and block reports arrive in difficult orders, failover into safe mode, replication queue suppression, `isInSafeMode` routing, open-file recovery after crash, snapshot trash root creation, and transition restrictions when safe mode should block active or observer state.

## Important APIs, Types, And Functions
The fixture starts a two-NameNode, three-DataNode cluster with small blocks, frequent heartbeats and edit tailing, and snapshot trash disabled. Key helpers are `restartStandby`, `restartActive`, `assertSafeMode`, and `banner`. Tests include `testClientRetrySafeMode`, `testEnterSafeModeInANNShouldNotThrowNPE`, `testEnterSafeModeInSBNShouldNotThrowNPE`, block-added/removed variants, `testAppendWhileInSafeMode`, `testComplexFailoverIntoSafemode`, `testSafeBlockTracking`, `testBlocksAddedWhileStandbyIsDown`, `testNoPopulatingReplQueuesWhenExitingSafemode`, `testNoPopulatingReplQueuesWhenStartingActiveInSafeMode`, `testIsInSafemode`, `testOpenFileWhenNNAndClientCrashAfterAddBlock`, `testSafeModeExitAfterTransition`, `testNameNodeCreateSnapshotTrashRootOnHASetup`, and transition-blocking tests for active/observer.

## Control Flow
The tests create and delete block-heavy files, roll edit logs, restart active or standby NameNodes with long safe mode extension, trigger block reports/deletion reports, wait for standby catch-up, and assert safe/total block counts through safe mode status strings. Append tests move blocks between under-construction and completed states. Crash recovery manually calls `addBlock` to create a block known only to the NameNode, restarts NameNode and DataNode, then opens and recovers the lease. Transition tests enter safe mode manually and expect configured failures for active or observer transitions.

## State And Persistence
Persistent state includes HDFS files, edits, fsimages, block replicas, snapshot trash roots, and leases. Transient state includes startup safe mode flags, manual safe mode flags, safe and total block counters, minimum live DataNode thresholds, pending deletion and replication queues, missing block counts, standby pending messages, and client last active routing.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `DFSTestUtil`, `HATestUtil`, `NameNodeAdapter`, `BlockManagerTestUtil`, `DFSClientAdapter`, `DFSOutputStream`, `DistributedFileSystem`, `SafeModeAction`, `LambdaTestUtils`, and `SubjectInheritingThread`. The suite connects safe mode with HA failover, block manager accounting, edit tailing, DataNode reporting, client retry, snapshot support, and lease recovery.

## Risks
This is a high-risk area because safe mode accounting depends on ordering among edits, full block reports, incremental block received/deletion reports, and HA transitions. Regressions can leave standby stuck in safe mode, count safe blocks below zero, populate replication queues too early, mark blocks missing during startup, or allow unsafe active/observer transitions. Several assertions parse human-readable safe mode strings, making message changes visible test breaks.

## Test Signals
Signals include successful delayed client mkdir after safe mode exit, safe mode status matching expected safe/total counts, no NPE from repeated enter-safe-mode calls, zero under-replicated/pending-replication queues in standby safe mode paths, correct standby exception for direct `isInSafeMode`, successful lease recovery after crash, snapshot `.Trash` creation only when enabled on the active, and expected `ServiceFailedException` when configured safe mode prevents active or observer transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHASafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAStateTransitions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAStateTransitions.java

## Purpose
`TestHAStateTransitions` validates active, standby, and failover state transitions for NameNodes. It covers single-node active/standby flip-flops, idempotent transitions, manual failover/failback, transition synchronization with concurrent writers, lease renewal, delegation token continuity, federated HA, empty edit-log failover, delegation secret-manager lifecycle, and active-detection utilities.

## Important APIs, Types, And Functions
Important tests include `testTransitionActiveToStandby`, `testTransitionToCurrentStateIsANop`, `testManualFailoverAndFailback`, `testTransitionSynchronization`, `testLeasesRenewedOnTransition`, `testDelegationTokensAfterFailover`, `testManualFailoverFailbackFederationHA`, `testFailoverWithEmptyInProgressEditLog`, `testFailoverWithEmptyInProgressEditLogWithHeader`, `testSecretManagerState`, and `testIsAtLeastOneActive`. Helpers include `testManualFailoverFailback`, `createEmptyInProgressEditLog`, `addCrmThreads`, `isDTRunning`, and `banner`.

## Control Flow
The suite starts HA clusters, moves NameNodes through active and standby, performs namespace mutations, and verifies the resulting namespace across failovers. Synchronization testing delays the FSNamesystem write lock and runs many client mkdir/delete loops while another thread toggles active/standby. Lease testing opens a file, waits for standby catch-up, then fails over and checks lease renewal timestamps. Empty edit-log tests simulate a crash during log roll by creating empty or header-only in-progress shared edit files before activating the standby. Secret-manager testing walks the active/standby and safe-mode state matrix to assert delegation token secret manager starts only in active, non-safe-mode state.

## State And Persistence
Persistent state includes directories, files, shared edit-log files, federated namespace contents, and delegation token edits. Transient state includes HA service state, cache replication monitor threads, FSNamesystem locks, open-file leases, secret-manager running state, safe mode state, and `ClientProtocol` proxies to all NameNodes.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `HATestUtil`, `NameNodeAdapter`, `NameNodeAdapterMockitoUtil`, `EditLogFileOutputStream`, `StorageDirectory`, `HAUtil`, `DFSUtil`, `MultithreadedTestUtil`, `UserGroupInformation`, and HDFS client APIs. The tests integrate state transition RPCs with namespace mutation, edit-log recovery, federation, tokens, leases, and utility proxy enumeration.

## Risks
Incorrect transition locking can allow writes while a NameNode is between states. Replaying a just-written segment can double-apply edits. Lease timestamps can be stale after failover, causing premature recovery. Empty in-progress logs can block failover if not treated as benign. Secret-manager lifecycle mistakes can issue or renew tokens from the wrong HA state.

## Test Signals
Signals include standby write rejection, namespace visibility/deletion across failover/failback, all cache replication monitor threads joining after shutdown, no concurrency exceptions during transition stress, lease timestamp advancement on failover, token renew/cancel after failover, successful federated namespace checks, activation despite empty in-progress logs, secret-manager running only in active non-safe-mode state, and `HAUtil.isAtLeastOneActive` matching cluster state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAStateTransitions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHarFileSystemWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHarFileSystemWithHA.java

## Purpose
`TestHarFileSystemWithHA` verifies that `HarFileSystem` can resolve archives stored on an HA HDFS logical URI whose underlying HDFS URI has no explicit port.

## Important APIs, Types, And Functions
The single test is `testHarUriWithHaUriWithNoPort`; helper `createEmptyHarArchive` creates the minimal HAR structure. It uses `HdfsConfiguration`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.setFailoverConfigurations`, `HATestUtil.configureFailoverFs`, `FileSystem.getDefaultUri`, `HarFileSystem.VERSION`, and `Path.getFileSystem`.

## Control Flow
The test starts a one-DataNode HA cluster, transitions NN0 active, configures HA failover, creates an empty HAR directory with `_masterindex` and `_index`, constructs a `har://hdfs-<logical-authority>/input.har` path, and asks that path for its filesystem.

## State And Persistence
Persistent state is the minimal HAR archive directory and metadata files in HDFS. Runtime state is the default logical HA URI in the configuration and the HAR filesystem URI parser/resolver.

## Dependencies And Integration Points
This test integrates HAR URI handling with HA logical HDFS authorities, default URI configuration, and failover filesystem setup.

## Risks
The bug class is URI parsing: HAR prepends `hdfs-` to the authority, and HA logical URIs often omit a physical port. Incorrect parsing can reject or misroute a valid archive path.

## Test Signals
The test passes if `Path.getFileSystem(conf)` succeeds for the constructed HAR path without throwing during resolution or archive initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHarFileSystemWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestInitializeSharedEdits.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestInitializeSharedEdits.java

## Purpose
`TestInitializeSharedEdits` verifies the `NameNode.initializeSharedEdits` command for file-based HA. It checks that missing shared edits prevent NameNode startup, initialization restores startup and standby catch-up, reinitialization works after namespace changes, no-shared-edits configurations are handled, existing dirs are not overwritten unexpectedly, and generic config keys are set.

## Important APIs, Types, And Functions
The fixture creates a two-NameNode HA cluster, enables standby reads, shortens log roll/tail periods, then shuts down both NameNodes and deletes the shared edits dir. Tests are `testInitializeSharedEdits`, `testFailWhenNoSharedEditsSpecified`, `testDontOverWriteExistingDir`, and `testInitializeSharedEditsConfiguresGenericConfKeys`. Helpers include `shutdownClusterAndRemoveSharedEditsDir`, `assertCannotStartNameNodes`, and `assertCanStartHaNameNodes`.

## Control Flow
The main test proves both NameNodes cannot restart without the shared edits dir, calls `NameNode.initializeSharedEdits`, restarts both NameNodes, transitions NN0 active, creates a path, and waits for standby catch-up. It then deletes shared edits again, reinitializes, and repeats HA startup and catch-up with another path. Other tests unset the shared edits key, call initialization with overwrite disabled twice, and verify `initializeSharedEdits` fills generic RPC address keys from suffixed HA config.

## State And Persistence
Persistent state includes local NameNode storage, the shared edits directory, edit logs copied/initialized into shared storage, and test directories under `/test`. The tests deliberately delete the shared edits directory and recreate it through the NameNode command.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `NameNode.initializeSharedEdits`, `HATestUtil`, `NameNodeAdapter`, `FileUtil.fullyDelete`, and HA state transition RPCs. It tests command-line/admin behavior through direct static method calls.

## Risks
Incorrect initialization can let NameNodes start with missing shared journals, overwrite existing data, or fail to configure generic keys needed by lower-level initialization. The test relies on expected startup IOException text for inaccessible storage directories.

## Test Signals
Signals include expected startup failures before initialization, `initializeSharedEdits` returning false on successful non-overwrite initialization, successful active write and standby visibility after initialization and reinitialization, true return when an existing dir is not overwritten, and generic `DFS_NAMENODE_RPC_ADDRESS_KEY` becoming populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestInitializeSharedEdits.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestLossyRetryInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestLossyRetryInvocationHandler.java

## Purpose
`TestLossyRetryInvocationHandler` verifies that enabling the test-only client option to drop NameNode responses does not prevent internal DFSClient instances inside NameNode/DataNode processes from being created, specifically when the NameNode trash emptier is enabled.

## Important APIs, Types, And Functions
The single test is `testStartNNWithTrashEmptier`. It uses `HdfsConfiguration`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HdfsClientConfigKeys.DFS_CLIENT_TEST_DROP_NAMENODE_RESPONSE_NUM_KEY`, and the `fs.trash.interval` configuration.

## Control Flow
The test enables trash emptier by setting a nonzero trash interval, configures client response dropping to two responses, starts a zero-DataNode HA cluster, waits for active services, and transitions NN0 active. Teardown shuts the cluster down.

## State And Persistence
There is little persistent HDFS state. Runtime state includes the HA NameNode process, internal trash emptier filesystem client, and lossy retry invocation behavior used by DFS clients.

## Dependencies And Integration Points
The test integrates HA startup, internal NameNode DFSClient construction, trash emptier scheduling/configuration, and lossy retry invocation handler test hooks.

## Risks
Client test hooks intended for external DFSClient tests can accidentally affect internal service clients. A regression can break NameNode startup or active transition when trash emptier creates a filesystem.

## Test Signals
The test passes if the cluster starts, waits active, and transitions to active without exceptions while both trash emptier and response dropping are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestLossyRetryInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestMultiObserverNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestMultiObserverNode.java

## Purpose
`TestMultiObserverNode` validates client read routing when an HA cluster has multiple Observer NameNodes. It verifies observer failover, shutdown/restart behavior, routing fallback to active when no observer is available, and fallback when observers lag behind the client's required state ID.

## Important APIs, Types, And Functions
The static fixture builds a QJM-backed observer cluster with two observers using `HATestUtil.setUpObserverCluster(conf, 2, 0, true)`, enables state context, and creates an observer-read `DistributedFileSystem` with `ObserverReadProxyProvider`. Tests are `testObserverFailover`, `testMultiObserver`, and `testObserverFallBehind`; helper `assertSentTo(int...)` uses `HATestUtil.isSentToAnyOfNameNodes`.

## Control Flow
The tests write via the active, roll and tail edits, then perform reads expected to hit either observer. They transition observers to standby one at a time, shut them down and restart them, transition them back to observer state, and assert routing moves among observers or back to active. The fall-behind test artificially sets the client's state ID far ahead and verifies a read goes to the active instead of stale observers.

## State And Persistence
Persistent state is a small directory tree under `/TestMultiObserverNode`. Runtime state includes active, standby, and observer roles for NameNode indices 0 through 3, client last-seen state ID, observer edit-tail position, and client proxy-provider routing cache.

## Dependencies And Integration Points
Dependencies include `MiniQJMHACluster`, `MiniDFSCluster`, `ObserverReadProxyProvider`, `HATestUtil`, `DistributedFileSystem`, and HA state transitions. The tests cover multi-observer routing over a QJM-backed HA setup.

## Risks
Routing bugs can strand reads on a standby, keep using a shutdown observer, or return stale data from an observer whose state ID is behind the client. Because any observer is acceptable in some assertions, the test focuses on eligible target sets rather than strict load-balancing.

## Test Signals
Signals include `assertSentTo(2, 3)` when both observers are valid, `assertSentTo(3)` or `assertSentTo(2)` when one observer is disabled, `assertSentTo(0)` when no observer or no sufficiently current observer is available, and successful cleanup/restart of both observers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestMultiObserverNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestNNHealthCheck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestNNHealthCheck.java

## Purpose
`TestNNHealthCheck` verifies health-monitor RPC behavior for HA NameNodes, including use of lifeline addresses, explicitly provided target addresses, resource-unavailable failures, and optional reporting of safe mode as unhealthy.

## Important APIs, Types, And Functions
Tests are `testNNHealthCheck`, `testNNHealthCheckWithLifelineAddress`, `testNNHAServiceTargetWithProvidedAddr`, and `testNNHealthCheckWithSafemodeAsUnhealthy`. Helper `doNNHealthCheckTest` installs `MockNameNodeResourceChecker` and obtains `NNHAServiceTarget.getHealthMonitorProxy`. The test uses `DFS_NAMENODE_LIFELINE_RPC_ADDRESS_KEY`, `DFS_NAMENODE_RPC_ADDRESS_KEY`, `HA_HM_RPC_TIMEOUT_KEY`, and `DFS_HA_NN_NOT_BECOME_ACTIVE_IN_SAFEMODE`.

## Control Flow
The basic tests start a no-DataNode HA cluster, replace NN0's resource checker, build an `NNHAServiceTarget`, assert its string contains the chosen RPC or lifeline address, call `monitorHealth` successfully, then set resources unavailable and expect a `HealthCheckFailedException` either directly or wrapped in `RemoteException`. The safe-mode test enables safe-mode-unhealthy behavior, enters safe mode through the filesystem, obtains the health monitor proxy, and expects a remote exception with the configured message.

## State And Persistence
The state under test is NameNode health-monitor RPC endpoint selection, resource-checker availability, lifeline address configuration, and safe mode status. There is no important persistent namespace state.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `NNHAServiceTarget`, `HAServiceProtocol`, `MockNameNodeResourceChecker`, `DFSUtil`, `LambdaTestUtils`, and safe mode filesystem APIs. The tests connect ZKFC-style health monitoring to NameNode resource and safe-mode status.

## Risks
Incorrect address selection can make ZKFC monitor the wrong RPC endpoint. Misreporting safe mode or resource exhaustion can cause unsafe failover decisions. Exception wrapping differs between local and remote paths, so the test accepts both direct and wrapped health failures where appropriate.

## Test Signals
Signals include target string containing the expected address, successful initial `monitorHealth`, expected message `The NameNode has no resources available` after resource failure, exact provided-address getters, and expected safe-mode-unhealthy remote exception text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestNNHealthCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverNode.java

## Purpose
`TestObserverNode` is the main Observer NameNode integration suite. It validates observer read routing, observer state transition restrictions, edit-tail requeue behavior, startup configuration, failover with observers, observer shutdown/restart, bootstrapping, safe mode and missing-block retry fallback, fsck, active-retry exceptions for writes, access-time redirects, sticky-active probing, state-ID consistency after mkdir races, deleted-dir listing, and empty file/dir reads.

## Important APIs, Types, And Functions
The static fixture enables NameNode state context, sets observer probe retry period to zero, and uses `HATestUtil.setUpObserverCluster(conf, 1, 1, true)` to create one active, one standby, and one observer over QJM. Tests include `testObserverRequeue`, `testNoActiveToObserver`, `testGetGroups`, `testNoObserverToActive`, `testSimpleRead`, `testConfigStartup`, `testFailover`, `testDoubleFailover`, `testObserverShutdown`, `testObserverFailOverAndShutdown`, `testBootstrap`, `testObserverNodeSafeModeWithBlockLocations`, `testObserverNodeBlockMissingRetry`, `testFsckWithObserver`, `testObserverRetryActiveException`, `testAccessTimeUpdateRedirectToActive`, `testStickyActive`, `testFsckDelete`, `testMkdirsRaceWithObserverRead`, `testGetListingForDeletedDir`, and `testSimpleReadEmptyDirOrFile`. Helpers include `assertSentTo`, `setObserverRead`, `ClientState`, and `MkDirRunner`.

## Control Flow
Most tests write or mutate through the active, roll and tail edits, then perform reads expected to go to the observer. They change HA states, shut down/restart the observer, disable observer startup, or disable observer reads to verify routing. Retry tests spy the observer `BlockManager` to return empty-located fake blocks so `open`, listing, and located-file APIs fall back to active. Requeue testing stops the observer edit tailer, schedules a read that blocks until edits are tailed, verifies RPC requeue metrics, then restores the tailer. The mkdir race delays active edit-log sync, runs multiple clients with separate DFS instances, and verifies last-seen state IDs are high enough to avoid stale observer reads.

## State And Persistence
Persistent state is a collection of test directories/files under `/TestObserverNode`, fsimage/edit-log state in QJM, and sometimes corrupt replica state. Transient state includes observer edit-tail progress, client last-seen state ID, proxy provider target choice, RPC requeue metrics, active/standby/observer HA states, safe mode status, block location responses, and observer probe timers.

## Dependencies And Integration Points
Dependencies include `MiniQJMHACluster`, `MiniDFSCluster`, `ObserverReadProxyProvider`, `HATestUtil`, `NameNodeAdapterMockitoUtil`, `NameNodeRpcServer`, `RpcMetrics`, `BlockManager`, `TestFsck`, `BootstrapStandby`, `GetGroups`, `HadoopExecutors`, Mockito, and `LambdaTestUtils`. The suite ties Observer NameNode behavior to client routing, state IDs, edit tailing, block location semantics, fsck, admin tools, and HA transitions.

## Risks
Observer reads are correctness-sensitive: a client must not read stale data from an observer behind its last seen state, writes must be retried on active, reads that need block locations or atime updates may need active fallback, and observer restarts must not leave clients stuck on dead targets. The tests use timing, scheduled tasks, and Mockito spies, so race windows and metrics timing are important.

## Test Signals
Signals include `assertSentTo` matching active or observer indices, expected `ServiceFailedException` for invalid transitions, RPC requeue count increment and eventual file status, successful `GetGroups` and fsck runs, healthy/corrupt fsck output as appropriate, `ObserverRetryOnActiveException` for direct observer write, active fallback for atime or missing-block cases, no stale read after mkdir race, expected `FileNotFoundException` for deleted dirs, and observer handling of empty directories/files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverNode.java -->
