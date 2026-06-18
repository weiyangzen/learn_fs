# subset-b-007534 research

Grouped research for the Hadoop HDFS qjournal and security test sources in subset-b-007534. Each section preserves the original source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestSecureNNWithQJM.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestSecureNNWithQJM.java

Purpose: Integration test for running a secure NameNode with Quorum Journal Manager (QJM). It proves that Kerberos, SPNEGO, HTTPS-only HTTP policy, block access tokens, data transfer protection, and JournalNode authentication can coexist while edit logs are persisted through QJM.

Important APIs/types/functions: `MiniKdc`, `MiniJournalCluster`, `MiniDFSCluster`, `HdfsConfiguration`, `KeyStoreTestUtil`, `SecurityUtil`, `UserGroupInformation`, `startCluster()`, `restartNameNode()`, `doNNWithQJMTest()`, `testSecureMode()`, and `testSecondaryNameNodeHttpAddressNotNeeded()`.

Control flow: `@BeforeAll init()` creates a test directory, starts a KDC, creates host and HTTP principals, enables Kerberos authentication, configures HTTPS keystores, and sets all NameNode/DataNode/JournalNode principals and keytabs. Each test clones the base configuration, starts JournalNodes, sets `dfs.namenode.edits.dir` to the quorum URI, starts a MiniDFSCluster, writes directories, restarts the NameNode twice, and checks that the namespace edits survive. Cleanup closes the filesystem, shuts down DFS and Journal clusters, stops the KDC, deletes test files, and resets UGI.

State and persistence behavior: The persistent signal is edit-log durability through JournalNodes across NameNode restarts. Test directories hold KDC keytabs and SSL config. The secondary NameNode HTTP address is explicitly set to `null` in one test to show it is not required in this secure QJM path.

Dependencies and integration points: Integrates HDFS security configuration, Hadoop HTTP auth filters, SSL test utilities, MiniKdc, MiniJournalCluster quorum edit logs, and MiniDFSCluster namespace reload. It depends on local host principal resolution, with a Windows-specific `127.0.0.1` principal instance.

Risks: This test is environment-sensitive because Kerberos principal names, hostname lookup, SSL resources, and port allocation all have to line up. A regression could silently break secure QJM bootstrap or HTTPS edit-log serving even if insecure QJM tests pass.

Test signals: Passing tests show authenticated secure mode can write and replay edits via QJM, and that disabling the secondary NameNode HTTP address does not block startup or edit replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestSecureNNWithQJM.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/DirectExecutorService.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/DirectExecutorService.java

Purpose: Minimal test-only `ExecutorService` that executes submitted work synchronously in the calling thread. QJM tests use it to remove scheduler nondeterminism from `IPCLoggerChannel` calls.

Important APIs/types/functions: `DirectExecutorService`, nested `DirectFuture<V>`, `submit(Callable<T>)`, `execute(Runnable)`, `shutdown()`, `isShutdown()`, `isTerminated()`, and unsupported executor bulk operations.

Control flow: `submit(Callable)` checks the shutdown flag, invokes the callable immediately through `DirectFuture`, captures either the result or exception, and returns an already-complete `Future`. `Future.get()` rethrows captured exceptions as `ExecutionException`. `execute(Runnable)` simply runs the command inline.

State and persistence behavior: The only state is the synchronized `isShutdown` boolean. There is no thread pool, queue, cancellation, timeout scheduling, or persistent state.

Dependencies and integration points: Implements the JDK `ExecutorService` contract enough for QJM client tests. It is injected by spy logger factories so `IPCLoggerChannel` calls are serialized and deterministic.

Risks: This class intentionally does not implement most `ExecutorService` methods. Production code must not depend on it. `execute()` does not reject after shutdown, unlike `submit()`, so tests relying on production executor shutdown semantics should avoid it.

Test signals: Its value is indirect: QJM fault and spy tests become stable because futures complete synchronously and call ordering is predictable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/DirectExecutorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/SpyQJournalUtil.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/SpyQJournalUtil.java

Purpose: Test utility for constructing a spy-backed `QuorumJournalManager` and for installing deterministic `getJournaledEdits` behaviors on its underlying `AsyncLogger` instances.

Important APIs/types/functions: `createSpyingQJM(...)`, `mockJNWithEmptyOrSlowResponse(...)`, `spyGetJournaledEdits(...)`, `AsyncLogger.Factory`, `IPCLoggerChannel`, `DirectExecutorService`, Mockito spies, `Semaphore`, and `GetJournaledEditsResponseProto`.

Control flow: `createSpyingQJM` supplies an `AsyncLogger.Factory` that creates `IPCLoggerChannel` instances overriding `createSingleThreadExecutor()` to return `DirectExecutorService`, then wraps them in Mockito spies. `mockJNWithEmptyOrSlowResponse` configures three JournalNodes: one returns an empty response, one calls through normally, and one blocks until the other responses release a semaphore. `spyGetJournaledEdits` wraps the real method with a pre-hook.

State and persistence behavior: No durable state. The semaphore in the slow-response helper coordinates mocked asynchronous responses inside a single test.

Dependencies and integration points: Used by QJM client tests that need real JournalNode IPC behavior with observable or intercepted RPCs. It couples to `QuorumJournalManager.getLoggerSetForTests()` and `QJM_RPC_MAX_TXNS_DEFAULT`.

Risks: Mockito stubbing targets exact `fromTxId` and max-txn arguments, so tests can miss calls if constants or selection logic changes. Slow-response coordination can deadlock if expected calls are skipped.

Test signals: Supports tests proving QJM can choose a useful edit stream despite empty, slow, or abnormal JournalNode responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/SpyQJournalUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestEpochsAreUnique.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestEpochsAreUnique.java

Purpose: Validates that QJM writer epochs are strictly unique and increasing, both in normal operation and when JournalNode RPCs intermittently fail.

Important APIs/types/functions: `QuorumJournalManager.createNewUniqueEpoch()`, `AsyncLogger.getJournalState()`, `AsyncLogger.newEpoch(long)`, `FaultyLoggerFactory`, `SometimesFaulty<T>`, `MiniJournalCluster`, and `NamespaceInfo`.

Control flow: The test formats a MiniJournalCluster, then creates five sequential QJMs and asserts epochs 1 through 5. It then repeatedly creates QJMs with a `FaultyLoggerFactory`; failures in `getJournalState` and `newEpoch` are injected through immediate failed futures until one attempt succeeds. Each successful epoch must be greater than the last successful epoch, allowing gaps.

State and persistence behavior: Epoch promises are persisted by JournalNodes, so newly constructed QJMs observe and advance from previous epochs. The random fault generator is in-memory and affects only test RPC calls.

Dependencies and integration points: Exercises client-side epoch election against real JournalNodes using `IPCLoggerChannel` spies. It depends on QJM quorum behavior tolerating minority failures while preserving monotonicity.

Risks: Random injection means failures are expected, but the test loops until success; severe regressions could appear as long-running failures. It verifies ordering, not exact epoch increments under faults.

Test signals: Passing means QJM does not reuse epochs after partial failure and can skip ahead safely when some JournalNodes accepted higher promises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestEpochsAreUnique.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestIPCLoggerChannel.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestIPCLoggerChannel.java

Purpose: Unit-style tests for `IPCLoggerChannel`, the client-side per-JournalNode channel used by QJM to send edits, track queue size, handle out-of-sync failures, and register metrics.

Important APIs/types/functions: `IPCLoggerChannel`, `QJournalProtocol`, `sendEdits`, `startLogSegment`, `heartbeat`, `getQueuedEditsSize`, `LoggerTooFarBehindException`, `DefaultMetricsSystem`, and `DelayAnswer`.

Control flow: Setup builds an `IPCLoggerChannel` whose `getProxy()` returns a Mockito `QJournalProtocol`, sets a queue size limit of 1 MB, and seeds epoch 1. `testSimpleCall` verifies journal RPC arguments. `testQueueLimiting` blocks mock journal calls, fills the byte-accounted queue, expects the next send to fail, then releases the delay and waits for queue drain. `testStopSendingEditsWhenOutOfSync` injects an IOException, verifies the channel enters out-of-sync state, sends a heartbeat instead of more edits, then clears state on `startLogSegment`. `testMetricsRemovedOnClose` checks metrics source removal.

State and persistence behavior: In-memory state includes queued edit byte count, out-of-sync flag, epoch, and registered metrics. No on-disk state is used here.

Dependencies and integration points: Tests the contract between QJM client code and `QJournalProtocol` RPCs. Metrics integration is checked through the Hadoop metrics system.

Risks: Queue accounting regressions can cause unbounded memory use when a JournalNode is slow. Out-of-sync handling is critical because continuing to send edits after missed batches corrupts a JournalNode's local log sequence.

Test signals: Assertions prove correct RPC shape, queue rejection threshold, heartbeat fallback while disabled, re-enable on segment roll, and metrics cleanup on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestIPCLoggerChannel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQJMWithFaults.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQJMWithFaults.java

Purpose: Exhaustive and randomized fault-injection tests for QJM writer recovery. It verifies that acknowledged edits are recoverable after dropped RPCs, JournalNode outages, and Paxos persistence faults.

Important APIs/types/functions: `QuorumJournalManager`, `MiniJournalCluster`, `QJMTestUtil.recoverAndReturnLastTxn`, `writeSegmentUntilCrash`, `InvocationCountingChannel`, `RandomFaultyChannel`, `WrapEveryCall`, `JournalFaultInjector`, `failIpcNumber`, and `RAND_SEED_PROPERTY`.

Control flow: `determineMaxIpcNumber()` runs a no-fault workload and counts RPCs. `testRecoverAfterDoubleFailures` iterates all pairs of single dropped RPCs on two loggers, writes two segments, records last acknowledged txid, then creates a fresh writer to recover and continue. `testRandomized` runs many writer iterations against channels that randomly flip up/down and inject faults around `acceptRecovery`; after each recovery it asserts the recovered txid is at least the last acknowledged txid. `testUnresolvableHostName` asserts bad QJM hostnames fail early.

State and persistence behavior: Real JournalNode edit logs and Paxos recovery files are persisted in the MiniJournalCluster. Test-only channel state counts RPCs and tracks injected failures. `JournalFaultInjector.instance` is replaced with a Mockito mock to simulate disk faults before or after Paxos data persistence.

Dependencies and integration points: Integrates real IPC, JournalNode storage, QJM quorum selection, edit-log segment recovery, and fault injection hooks. Uses `DirectExecutorService` to keep RPC sequencing deterministic.

Risks: Randomized paths can expose rare ordering bugs but are expensive and seed-sensitive. The central correctness risk is data loss: recovery must never return a txid lower than an acknowledged write.

Test signals: Passing tests demonstrate that QJM can recover after majority-interrupting failures, tolerate node flapping, preserve acknowledged edits, and resume writing after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQJMWithFaults.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumCall.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumCall.java

Purpose: Tests the generic `QuorumCall` future aggregation helper used by QJM to wait for enough responses, successes, or failures across JournalNodes.

Important APIs/types/functions: `QuorumCall.create`, `waitFor`, `countResponses`, `getResults`, Guava `SettableFuture`, `FakeTimer`, and timeout handling.

Control flow: `testQuorums` creates three futures, completes them in success/failure/success order, waits for response and success thresholds, verifies result ordering through a sorted map, and asserts impossible success thresholds time out. `testQuorumFailsWithoutResponse` verifies waiting for success without any completion times out. `testQuorumSucceedsWithLongPause` uses a `FakeTimer` that advances sharply and later completes a future to ensure a single long pause does not cause premature timeout if progress occurs.

State and persistence behavior: All state is in-memory future completion and timer state. There is no filesystem or RPC dependency.

Dependencies and integration points: This is a low-level client utility test; QJM operations depend on these semantics for quorum thresholds, diagnostics, and timeout behavior.

Risks: Incorrect response counting or timeout calculation can cause QJM to hang, fail too early, or accept too few JournalNode responses. Timer behavior is especially important under GC pauses or scheduler stalls.

Test signals: Passing tests confirm response counts, success result collection, timeout failure, and tolerance of a simulated long pause before eventual completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumCall.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManager.java

Purpose: Functional test suite for `QuorumJournalManager` against real MiniJournalCluster instances. It covers writes, reads, failover recovery, Paxos edge cases, purging, RPC tailing, fallback read paths, and qjournal URI resolution.

Important APIs/types/functions: `QuorumJournalManager`, `AsyncLoggerSet`, `IPCLoggerChannel`, `MiniJournalCluster`, `writeSegment`, `verifyEdits`, `recoverUnfinalizedSegments`, `selectInputStreams`, `finalizeLogSegment`, `purgeLogsOlderThan`, `SegmentStateProto`, `RemoteEditLogManifest`, and `Util.getAddressesList`.

Control flow: Setup disables slow IPC retry/caching, enables in-progress tailing, starts a cluster, creates spy loggers, formats, and recovers epoch 1. Tests write finalized and in-progress segments, read while another writer is active, stop/restart JournalNodes, inject send/finalize/start/accept failures, and create fresh QJMs to simulate failover. Helper methods verify quorum-finalized files, wait for pending calls, create special out-of-sync states, and spy on read RPCs.

State and persistence behavior: JournalNode current directories store finalized edits, in-progress edits, `.empty` moved-aside files, and Paxos accepted recovery records. Tests assert exact file names and quorum presence after recovery and purging. Client-side state includes epochs, committed txid, pending async calls, and selected input streams.

Dependencies and integration points: Integrates QJM client logic with JournalNode storage, file journal scanning, RPC edit retrieval, manifest-based streaming fallback, domain-name resolution, metrics thread behavior, and `SpyQJournalUtil`.

Risks: The suite targets high-risk failure modes: choosing an unsafe recovery length, truncating newer segments because of stale accepted Paxos data, leaking read threads for dead JNs, reading uncommitted transactions, and mishandling gaps when one JN misses segments.

Test signals: Passing tests prove quorum writes/readback, failover recovery across multiple divergence scenarios, accepted-recovery ordering, purge cleanup of edits and Paxos files, durable-transaction filtering, RPC read fallback, JN jitter handling, restart handling, and resolver behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManagerUnit.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManagerUnit.java

Purpose: Pure unit tests for `QuorumJournalManager` using mocked `AsyncLogger` instances. It validates quorum thresholds, output stream behavior, edit batching, auto-sync, and RPC-based edit stream selection without running JournalNodes.

Important APIs/types/functions: `futureReturns`, `futureThrows`, `createLogSegment`, `QuorumOutputStream`, `FSEditLog`, `selectInputStreams`, `getJournaledEdits`, `GetJournaledEditsResponseProto`, `EditLogFileOutputStream.writeHeader`, and `QJMTestUtil`.

Control flow: Setup creates three mock loggers, stubs `getJournalState`, `newEpoch`, and `format`, then recovers unfinalized segments. Start-segment tests check all-success, quorum-success, and quorum-failure behavior. Write tests create a quorum output stream, write operations, use `setReadyToFlush`, and verify `sendEdits` batches. RPC read tests return identical, mismatched, slow, failed, or empty edit responses and assert the selected stream contents. The FSEditLog test sets a small buffer so logging many mkdir edits triggers an automatic sync to QJM.

State and persistence behavior: No real disk state. Edit-log bytes are synthesized in memory with valid headers and transaction payloads. Mock futures represent asynchronous JournalNode responses.

Dependencies and integration points: Exercises QJM logic around `AsyncLogger`, `QuorumOutputStream`, HDFS `FSEditLog`, and edit-log serialization. The auto-sync regression test links QJM buffering to NameNode edit logging behavior.

Risks: Incorrect mock expectations can hide integration issues, but the suite gives fast coverage of quorum math and batching. Buffer capacity must stay below IPC maximum; the test asserts oversize capacity is rejected.

Test signals: Passing tests show quorum start/write semantics, plain-text reporting, correct send ranges, buffer-capacity validation, auto-sync on full buffer, committed-txid propagation, and robust RPC tailing decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManagerUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestSegmentRecoveryComparator.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestSegmentRecoveryComparator.java

Purpose: Unit test for `SegmentRecoveryComparator`, which ranks JournalNode `prepareRecovery` responses during QJM segment recovery.

Important APIs/types/functions: `SegmentRecoveryComparator.INSTANCE`, `PrepareRecoveryResponseProto`, `SegmentStateProto`, Mockito `AsyncLogger` placeholders, and map entries keyed by logger.

Control flow: The test builds in-progress segment responses with different end txids, an in-progress response with an accepted epoch, and a finalized response. It compares pairs and asserts the ordering rules: equal to self, longer in-progress segment wins over shorter in-progress segment, and finalized segment wins over longer or accepted in-progress segment.

State and persistence behavior: No persistent state. The test models recovery metadata purely with protobuf objects.

Dependencies and integration points: The comparator is used by QJM recovery to choose the safest segment state from multiple JournalNodes. Its ordering feeds directly into accept/finalize decisions.

Risks: A wrong comparison can select a stale or unsafe segment and either lose edits or reject valid finalized history. The test focuses on the core precedence rules but does not cover every epoch/accepted-value combination.

Test signals: Passing confirms finalized logs outrank in-progress logs, and length only decides among compatible in-progress candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestSegmentRecoveryComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/JournalTestUtil.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/JournalTestUtil.java

Purpose: Small server-side test utility for deliberately corrupting a `Journal`'s in-memory `JournaledEditsCache`.

Important APIs/types/functions: `JournalTestUtil`, `corruptJournaledEditsCache(long, Journal)`, `Journal.getJournaledEditsCache()`, and `JournaledEditsCache.getRawDataForTests(txid)`.

Control flow: The helper fetches the raw byte buffer containing the requested transaction id and mutates bytes at three repeating offsets: sets some bytes to zero, increments some by ten, and decrements others by ten.

State and persistence behavior: The mutation targets cache memory, not edit-log files. It simulates corrupt cached entries while leaving on-disk journal state unchanged.

Dependencies and integration points: Intended for tests that need cache corruption without constructing malformed edit logs on disk. It reaches into test-only cache accessors.

Risks: It depends on raw buffer layout and mutates bytes arbitrarily, so callers must only use it where corruption is the intended condition. It can make subsequent cache reads fail until the cache is refreshed or discarded.

Test signals: This file provides no tests itself; downstream tests use it as a fault-injection primitive for cache validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/JournalTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestGetJournalEditServlet.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestGetJournalEditServlet.java

Purpose: Tests requestor validation for `GetJournalEditServlet`, the HTTP endpoint used to fetch journal edit files.

Important APIs/types/functions: `GetJournalEditServlet`, `isValidRequestor`, `ServletConfig`, `HttpServletRequest`, `UserParam.NAME`, `UserGroupInformation`, and HDFS Kerberos principal configuration.

Control flow: `@BeforeAll` builds a security-aware `HdfsConfiguration`, sets auth-to-local rules mapping NameNode and JournalNode principals, configures nameservice and NameNode Kerberos principal, sets the login user to a JournalNode principal, and initializes the servlet. Tests then mock requests with no user, a NameNode Kerberos user, and a JournalNode user that relies on short-name fallback.

State and persistence behavior: No persistent data. Global UGI configuration and servlet static instance are initialized once for the class.

Dependencies and integration points: Integrates servlet request validation with Hadoop security name mapping, WebHDFS `UserParam`, and NameNode principal configuration.

Risks: Authorization bugs could allow unauthenticated edit-log downloads or reject valid NameNode/JournalNode sync requests. Auth-to-local rule changes can alter expected short names.

Test signals: Passing tests prove unauthenticated requests are rejected, configured NameNode principals are allowed, and JournalNode short-name fallback remains accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestGetJournalEditServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournal.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournal.java

Purpose: Server-side unit/integration tests for `Journal`, the persistent edit-log and Paxos state object inside a JournalNode.

Important APIs/types/functions: `Journal`, `JNStorage`, `RequestInfo`, `newEpoch`, `startLogSegment`, `journal`, `finalizeLogSegment`, `getSegmentInfo`, `getJournaledEdits`, `JournalOutOfSyncException`, `StorageErrorReporter`, and `NameNodeLayoutVersion`.

Control flow: Setup deletes a test log directory, enables in-progress tailing, creates and formats a `Journal`. Tests cover scanning garbage/future-layout logs, moving failed preallocation files aside as `.empty`, epoch promise rejection, committed txid tracking, restart persistence, format reset, empty segment epoch reporting, storage locking, finalize validation, aborting old in-progress segments on a later start, preventing unsafe segment overwrite, namespace mismatch, force/non-force format, and cache reads.

State and persistence behavior: The test asserts durable storage contents: epoch files, writer epoch, namespace info, finalized and in-progress edit files, lock files, moved-aside empty files, and cache data. Reconstructing `Journal` from disk must preserve storage metadata and prevent invalid finalization.

Dependencies and integration points: Integrates edit-log serialization, `FileJournalManager` scanning, HDFS storage locking, QJM request epoch checks, cache serving for `getJournaledEdits`, and storage error reporting.

Risks: This is a critical data-integrity surface. Regressions can permit stale-epoch writes, unsafe overwrites, false finalization, namespace mixing, or startup failure after partially allocated edit files.

Test signals: Passing confirms Journal persistence, epoch monotonicity, namespace verification, lock release, safe segment lifecycle handling, strict finalization checks, and correct cached edit responses with layout headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNode.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNode.java

Purpose: Tests `JournalNode` process behavior, including directory selection, RPC/HTTP services, metrics, Paxos acceptor behavior, startup failure handling, syncer startup configuration, federation, and handler-count configuration.

Important APIs/types/functions: `JournalNode`, `JournalNodeRpcServer`, `IPCLoggerChannel`, `MiniDFSCluster`, `JNStorage`, `MetricsAsserts`, `getOrCreateJournal`, `getJournalSyncerStatus`, `getHttpServerURI`, `prepareRecovery`, `acceptRecovery`, and `DFS_JOURNALNODE_*` configuration keys.

Control flow: Setup builds a configuration tailored by test method name, starts a JournalNode on dynamic ports, creates/formats journals, and opens an IPC logger channel. Tests verify per-nameservice, common, and default edit directories; metric tags and counters; journal writes and lag gauges; epoch transition segment info; HTTP `/jmx` and `/getJournal`; Paxos prepare/accept persistence and epoch rejection; invalid edit directory startup failures; clean stop on bind failure; optional JournalNodeSyncer startup with disabled, bad URI, and federation configs; and RPC handler count fallback.

State and persistence behavior: Journal storage directories are formatted and checked by path. Metrics counters/gauges reflect writes and lag. Paxos accepted recovery state is persisted and visible in a later epoch. HTTP edit retrieval returns finalized edit bytes.

Dependencies and integration points: Integrates JournalNode daemon lifecycle, RPC server, HTTP server, metrics system, federation configuration, static host resolution, QJM IPC client, and JournalNodeSyncer selection.

Risks: Misconfiguration can place edit logs under the wrong namespace, leak partially started services, expose bad HTTP data, fail to persist Paxos promises, or start syncers against the wrong quorum URI.

Test signals: Passing indicates correct JournalNode startup, storage layout, metrics, HTTP edit serving, Paxos acceptor semantics, config validation, syncer gating, and handler-count enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeHttpServerXFrame.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeHttpServerXFrame.java

Purpose: Tests that JournalNode HTTP responses honor the global HDFS X-Frame-Options configuration.

Important APIs/types/functions: `MiniJournalCluster`, `JournalNode.getHttpServerURI()`, `DFS_XFRAME_OPTION_ENABLED`, `HttpServer2.XFrameOption.SAMEORIGIN`, and `HttpURLConnection`.

Control flow: Each test creates a one-node MiniJournalCluster with X-Frame enabled or disabled, opens an HTTP connection to the JournalNode root URI, and reads the `X-FRAME-OPTIONS` response header. Cleanup shuts the cluster down.

State and persistence behavior: No edit-log persistence is relevant. State is the HTTP server configuration applied at cluster creation.

Dependencies and integration points: Integrates JournalNode HTTP server construction with Hadoop HTTP security header configuration.

Risks: Missing or unexpected X-Frame headers can weaken clickjacking protections or break clients expecting the header to be absent when disabled.

Test signals: Passing confirms enabled clusters send a SAMEORIGIN X-Frame header and disabled clusters omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeHttpServerXFrame.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeMXBean.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeMXBean.java

Purpose: Tests the JMX/MXBean exposure of JournalNode status, identity, version, cluster IDs, start time, and storage information.

Important APIs/types/functions: `JournalNodeMXBean`, platform `MBeanServer`, ObjectName `Hadoop:service=JournalNode,name=JournalNodeInfo`, `getJournalsStatus`, `getHostAndPort`, `getClusterIds`, `getStorageInfos`, and Jetty JSON serialization.

Control flow: Setup starts a one-node MiniJournalCluster. The test reads MXBean attributes before formatting a journal and confirms the nameservice is absent. It formats journal `ns1`, reads `JournalsStatus` again, compares the JSON to `jn.getJournalsStatus()`, and verifies host/port, cluster IDs, start time, version, and storage info. It then restarts a cluster without formatting and confirms the MXBean still reports the persisted journal status.

State and persistence behavior: Formatting creates persistent storage info containing namespace ID, cluster ID, and creation time. The restart-without-format path proves storage status survives daemon restart.

Dependencies and integration points: Integrates JournalNode with Hadoop metrics/JMX registration, JSON status generation, and MiniJournalCluster storage lifecycle.

Risks: Incorrect MXBean data can break monitoring and operational diagnosis. Status must distinguish lazily created unformatted journals from formatted persistent journals.

Test signals: Passing validates MXBean attribute parity with JournalNode methods and persistent storage status across restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeRespectsBindHostKeys.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeRespectsBindHostKeys.java

Purpose: Verifies that JournalNode RPC, HTTP, and HTTPS listeners honor explicit bind-host configuration keys.

Important APIs/types/functions: `DFS_JOURNALNODE_RPC_BIND_HOST_KEY`, `DFS_JOURNALNODE_HTTP_BIND_HOST_KEY`, `DFS_JOURNALNODE_HTTPS_BIND_HOST_KEY`, `MiniJournalCluster`, `JournalNodeRpcServer`, `KeyStoreTestUtil`, `HttpConfig.Policy.HTTPS_ONLY`, and `HdfsConfiguration`.

Control flow: Each test first starts a one-node cluster without the bind-host key and asserts it does not bind wildcard `0.0.0.0`. It then sets the relevant bind-host key to wildcard, starts another cluster, and verifies the listener address uses wildcard. HTTPS setup creates SSL config and switches the HTTP policy to HTTPS-only before checking the HTTPS address.

State and persistence behavior: No journal persistence is under test. Temporary SSL keystore/config files are created for the HTTPS path.

Dependencies and integration points: Integrates JournalNode network listener setup, MiniJournalCluster builder, SSL test utilities, and HDFS HTTP policy configuration.

Risks: Binding to the wrong interface can expose JournalNode services unexpectedly or make them unreachable in multi-homed deployments. HTTPS setup is sensitive to SSL resource paths.

Test signals: Passing confirms default loopback/non-wildcard behavior and explicit wildcard binding for RPC, HTTP, and HTTPS listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeRespectsBindHostKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeSync.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeSync.java

Purpose: Slow HA integration suite for JournalNode sync repair. It verifies that `JournalNodeSyncer` restores missing edit logs after deletion, downtime, formatting, disk wipe, and rolling upgrade scenarios.

Important APIs/types/functions: `MiniQJMHACluster`, `MiniDFSCluster`, `MiniJournalCluster`, `JournalNodeSyncer`, `generateEditLog`, `deleteEditLog`, `deleteEditLogsFromRandomJN`, `editLogExists`, `jnFormatted`, `DFS_JOURNALNODE_ENABLE_SYNC_KEY`, `DFS_JOURNALNODE_SYNC_INTERVAL_KEY`, and rolling-upgrade APIs.

Control flow: Setup enables JournalNode sync and sync-format, starts a two-NameNode HA cluster backed by QJM, transitions NN0 active, and captures namesystem state. Tests verify self-exclusion for same-host multi-port and wildcard URIs, then create finalized edit segments, delete selected segment files from one or more JournalNodes, and wait for sync to restore them. Downtime tests stop a JournalNode while edits roll, restart it, roll another edit to advance committed txid, and wait for missing files. Format and disk-wipe tests ensure the syncer can reformat and refill storage. Rolling upgrade test prepares, restarts standby with rolling-upgrade flags, fails over, deletes logs during upgrade, verifies repair, and finalizes upgrade.

State and persistence behavior: The primary state is finalized edit-log files in each JournalNode current directory and journal formatting metadata. Tests delete actual files and require them to reappear. Metrics such as `NumEditLogsSynced` validate repair path usage when QJournal queueing is disabled.

Dependencies and integration points: Integrates HA NameNode edit rolling, JournalNodeSyncer HTTP/RPC download, QJM committed txid behavior, MiniQJMHACluster topology, storage formatting, and rolling upgrade state.

Risks: Sync repair is a data availability mechanism; failures can leave rejoined or reformatted JournalNodes permanently behind. Tests are slow and timing-sensitive because they poll background sync.

Test signals: Passing proves syncers start when configured, avoid syncing from self, restore single/multiple/discontinuous/random missing logs, recover after downtime and format, preserve repair during rolling upgrades, and update format state after disk wipe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournaledEditsCache.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournaledEditsCache.java

Purpose: Tests `JournaledEditsCache`, the in-memory cache used by `Journal` to serve recent edit logs through RPC for in-progress tailing.

Important APIs/types/functions: `JournaledEditsCache`, `storeEdits`, `retrieveEdits`, `CacheMissException`, `getCapacity`, `DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY`, `DFS_JOURNALNODE_EDIT_CACHE_SIZE_FRACTION_KEY`, `EditLogFileOutputStream.writeHeader`, and `QJMTestUtil.createTxnData/createGabageTxns`.

Control flow: Setup sizes the cache to hold 100 single-transaction edit payloads. Tests store segments and retrieve leading, trailing, boundary, off-boundary, over-end, and multi-segment ranges. Capacity tests exceed cache size with multiple additions or one oversized batch and assert older ranges miss. Layout-version tests ensure future-layout and mixed-layout ranges return appropriate headers or cache misses. Gap, uninitialized, malformed input, and config tests verify error and capacity paths. Helpers assemble expected header plus transaction bytes and compare returned buffers.

State and persistence behavior: State is entirely in-memory cache buffers and layout-version metadata. Temporary test directory cleanup is incidental.

Dependencies and integration points: Supports `Journal.getJournaledEdits` and QJM RPC tailing. It depends on edit-log transaction serialization and layout headers matching NameNode edit-log format.

Risks: Incorrect cache boundaries can return missing, duplicated, or uncommitted edits to observer/standby readers. Mixed layout versions must not be merged in one response. Oversized batches must not permanently poison later valid cache additions.

Test signals: Passing confirms range slicing, cache miss amounts, eviction behavior, gap detection, malformed request rejection, layout-header correctness, and config precedence for capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournaledEditsCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationToken.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationToken.java

Purpose: Tests HDFS delegation token lifecycle, API integration, metrics, UGI identity behavior, safe-mode interaction, stable string formatting, and token expiration logging.

Important APIs/types/functions: `DelegationTokenSecretManager`, `DelegationTokenIdentifier`, `MiniDFSCluster`, `DistributedFileSystem.addDelegationTokens`, `WebHdfsFileSystem.addDelegationTokens`, `NameNodeAdapter.getDtSecretManager`, `UserGroupInformation`, `Credentials`, `AbstractDelegationTokenSecretManager.logExpireTokens`, and `KerberosName.setRules`.

Control flow: Setup starts a no-DataNode MiniDFSCluster with short max lifetime, renew interval, always-use delegation tokens, and auth-to-local rules. Tests generate tokens directly or through DFS/WebHDFS, verify unauthorized renew/cancel failures, authorized renew/cancel success, expiration after sleep, metrics count changes, duplicate token suppression in credentials, renewal/cancel under long and short UGI names, identifier UGI caching, secret-manager start/stop around safe mode, stable `toString`, and robust expire-token logging after auth-to-local rules change.

State and persistence behavior: Delegation tokens live in the NameNode secret manager and namesystem metrics. Safe-mode test restarts the NameNode and verifies secret-manager running state follows safe mode because key updates write edit logs. Credentials hold client-side token copies.

Dependencies and integration points: Integrates NameNode security, DFS API, WebHDFS API, UGI doAs, Kerberos name rules, namesystem metrics, safe mode, and token secret manager internals.

Risks: Token bugs can allow unauthorized renewal/cancel, leak expired tokens, fail clients using WebHDFS/DFS APIs, or write edit logs during safe mode. Rule changes can make previously loaded tokens hard to stringify/log.

Test signals: Passing confirms lifecycle authorization, expiry, metrics, DFS/WebHDFS token acquisition, UGI identity caching, safe-mode gating of the secret manager, stable formatting, and expiration logging resilience.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationTokenForProxyUser.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationTokenForProxyUser.java

Purpose: Tests HDFS delegation token and WebHDFS behavior when a real user impersonates a proxy user.

Important APIs/types/functions: `UserGroupInformation.createProxyUserForTesting`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, `DefaultImpersonationProvider`, `MiniDFSCluster`, `DelegationTokenIdentifier`, `WebHdfsTestUtil`, `Whitebox.setInternalState`, and WebHDFS create/append/status operations.

Control flow: `@BeforeAll` configures delegation token lifetimes, proxy superuser group and IP allowlists, starts a MiniDFSCluster, refreshes proxy user rules, creates real and proxy UGIs. `configureSuperUserIPAddresses` enumerates local interfaces and adds loopback/canonical host entries. `testDelegationTokenWithRealUser` obtains delegation tokens inside `proxyUgi.doAs`, decodes the identifier, and asserts effective user is `ProxyUser` with real user `RealUser`. `testWebHdfsDoAs` opens WebHDFS as the real user, swaps its internal UGI to the proxy UGI, and verifies home directory, file creation, append, and ownership reflect the proxy user.

State and persistence behavior: Cluster filesystem state includes a test file owned by the proxy user. Token identifiers encode real/effective user identity. Global proxy-user config is refreshed once.

Dependencies and integration points: Integrates proxy authorization, local network address detection, HDFS delegation tokens, WebHDFS doAs behavior, filesystem permissions, and UGI identity propagation.

Risks: Proxy-user regressions can issue tokens to the wrong identity or perform WebHDFS writes as the real user instead of the effective user. Network-interface allowlists make setup environment-sensitive.

Test signals: Passing confirms token identifiers preserve real/effective user relationship and WebHDFS operations execute with proxy ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationTokenForProxyUser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/SecurityTestUtil.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/SecurityTestUtil.java

Purpose: Test helper exposing block token expiration and lifetime controls for security tests.

Important APIs/types/functions: `SecurityTestUtil`, `isBlockTokenExpired(Token<BlockTokenIdentifier>)`, `setBlockTokenLifetime(BlockTokenSecretManager, long)`, `BlockTokenSecretManager.isTokenExpired`, and `BlockTokenSecretManager.setTokenLifetime`.

Control flow: The helper delegates directly to package-relevant `BlockTokenSecretManager` methods. One method checks whether a given block token is expired; the other mutates the token lifetime on a supplied secret manager.

State and persistence behavior: No persistent state. `setBlockTokenLifetime` changes in-memory configuration on the provided secret manager, affecting tokens generated or validated by that manager in tests.

Dependencies and integration points: Used by HDFS block-token tests that need access to expiration behavior without duplicating secret-manager internals.

Risks: Because it exposes mutable lifetime control, tests must reset or isolate secret managers to avoid cross-test leakage. It is intentionally test-scope utility code, not a production API.

Test signals: This file has no direct assertions; downstream tests use it to force or observe block-token expiry scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/SecurityTestUtil.java -->
