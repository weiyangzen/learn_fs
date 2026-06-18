# subset-b-007479 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLogger.java

Purpose: Defines the asynchronous client-side abstraction over a single remote JournalNode. It mirrors `QJournalProtocol` operations but returns `ListenableFuture` results and lets implementations construct `RequestInfo` with epoch, IPC serial, and committed transaction context.

Important APIs/types/functions: `AsyncLogger.Factory` creates logger channels. Core methods cover journal lifecycle (`isFormatted`, `format`, `getJournalState`, `newEpoch`), write flow (`startLogSegment`, `sendEdits`, `finalizeLogSegment`, `purgeLogsOlderThan`), recovery (`prepareRecovery`, `acceptRecovery`, `buildURLToFetchLogs`), read/tailing (`getJournaledEdits`, `getEditLogManifest`), writer state (`setEpoch`, `setCommittedTxId`), upgrade/rollback operations, and `appendReport`.

Control flow: `AsyncLoggerSet` fans out calls to implementations, most commonly `IPCLoggerChannel`; each call returns immediately with a future, and quorum wait logic is handled outside this interface. The interface separates active-writer mutation calls from read/manifest calls but leaves executor ordering to implementations.

State and persistence behavior: The interface owns no state directly, but its `setEpoch` and `setCommittedTxId` calls define the state that implementations attach to durable JournalNode requests. Recovery URLs link RPC state to HTTP-served edit-log files.

Dependencies/integration: Integrated by `AsyncLoggerSet`, `QuorumJournalManager`, and `IPCLoggerChannel`; payload and response types come from qjournal protobufs, HDFS `NamespaceInfo`, `StorageInfo`, and `RemoteEditLogManifest`.

Risks: Implementations must preserve write ordering and correct `RequestInfo` sequencing; any future returned as null violates `QuorumCall` assumptions; stale epoch or committed-txid propagation can affect fencing and recovery safety.

Test signals: Mock/fake implementations should verify fan-out calls, future completion/failure behavior, epoch and committed-txid propagation, recovery URL generation, and close/report behavior after in-flight operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java

Purpose: Immutable wrapper around all `AsyncLogger` instances for one quorum journal. It fans out operations and provides majority-based wait semantics for write quorum operations.

Important APIs/types/functions: `setEpoch`, `getEpoch`, `setCommittedTxId`, `waitForWriteQuorum`, `getMajoritySize`, `getMajorityString`, `appendReport`, and boilerplate quorum-call factories for all `AsyncLogger` methods.

Control flow: Construction copies the logger list. Epoch can be established only once, then pushed to every logger. Write quorum waits return when all loggers answer, a majority succeeds, or too many failures make quorum impossible; after waiting, insufficient successes are converted to `QuorumException`. Fan-out methods build a map of logger to future and wrap it with `QuorumCall`.

State and persistence behavior: Tracks only `myEpoch`; persistent effects are on remote JournalNodes. `purgeLogsOlderThan` intentionally fire-and-forgets because failure to purge is not correctness critical.

Dependencies/integration: Used by `QuorumJournalManager` and `QuorumOutputStream`; depends on `QuorumCall`, `QuorumException`, and protobuf response types for recovery, manifests, and upgrades.

Risks: Majority math assumes an odd number of loggers for best availability; even counts are supported but reduce failure tolerance. Epoch establishment is one-shot, so manager reuse across writer epochs is not supported. Late future completions can mutate a `QuorumCall` after wait returns, though returned result maps are copied.

Test signals: Unit tests should cover majority thresholds for 1/3/5 nodes, timeout and interruption translation to `IOException`, too-many-failure exception formatting, one-shot epoch validation, and all fan-out wrappers creating one future per logger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannel.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannel.java

Purpose: Concrete `AsyncLogger` that talks to one JournalNode over Hadoop protobuf RPC and uses an HTTP endpoint for edit-log segment transfer during reads and recovery.

Important APIs/types/functions: Constructors wire journal id, namespace, RPC address, queue limit, executors, and metrics. Key methods include `createProxy`, `createReqInfo`, `sendEdits`, `startLogSegment`, `finalizeLogSegment`, `prepareRecovery`, `acceptRecovery`, `getJournaledEdits`, `getEditLogManifest`, `buildURLToFetchLogs`, `reserveQueueSpace`, `heartbeatIfNecessary`, and lag/report accessors.

Control flow: Write-like calls run on a single-thread executor to preserve FIFO ordering and IPC serial monotonicity; read/tailing calls run on a bounded parallel executor. `sendEdits` reserves bytes before enqueue, writes with `journal(createReqInfo(), ...)`, marks the channel out-of-sync on `IOException`, records latencies, and unreserves bytes when the future completes. If out of sync, later writes send periodic heartbeats but fail until a new segment starts.

State and persistence behavior: Client-local state includes epoch, monotonically increasing IPC serial, committed txid, queued edit bytes, highest acknowledged txid, lag timestamps, and cached JournalNode HTTP URL. Durable persistence happens remotely through RPCs; the committed-txid piggyback lets lagging JournalNodes skip fsync for already quorum-committed edits and validate recovery.

Dependencies/integration: Wraps `QJournalProtocolTranslatorPB` over `QJournalProtocolPB` using `ProtobufRpcEngine2`; integrates with `GetJournalEditServlet` path construction, `IPCLoggerChannelMetrics`, DFS qjournal timeout/queue/read-thread configs, and `SecurityUtil.doAsLoginUser`.

Risks: Queue overflow silently drops that logger from the current quorum attempt via `LoggerTooFarBehindException`; a stuck `RPC.stopProxy` can hang close; HTTP endpoint is learned lazily from state/manifest responses; out-of-sync status can persist until a segment roll; all write RPCs depend on strict executor ordering.

Test signals: Tests should cover queue-limit failures, out-of-sync transition and reset on new segment, heartbeat throttling, HTTP URL construction for both `fromURL` and legacy port responses, lag metric calculations, serial ordering, executor shutdown, and slow RPC latency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java

Purpose: Exposes writer-side metrics for one `IPCLoggerChannel` through Hadoop metrics.

Important APIs/types/functions: `create`, `unregister`, metric getters `isOutOfSync`, `getCurrentLagTxns`, `getLagTimeMillis`, `getQueuedEditsSize`, and latency mutators `addWriteEndToEndLatency` and `addWriteRpcLatency`.

Control flow: Construction reads percentile intervals from `HdfsConfiguration`, allocates quantile series for end-to-end write latency and RPC latency, and registers one source named from the remote address. Metric getters pull live channel values on demand.

State and persistence behavior: No durable state. Holds a volatile channel reference and in-memory quantile counters registered with `DefaultMetricsSystem`.

Dependencies/integration: Created by every `IPCLoggerChannel`; metric names depend on the JournalNode IP/port with IPv6 colons replaced for MBean compatibility.

Risks: Uses a fresh `HdfsConfiguration` rather than the channel's exact configuration, so percentile interval overrides must be visible through default config loading. Registration names collide if multiple channels target the same address in the same metrics system.

Test signals: Verify source naming for IPv4/IPv6, quantile creation with configured intervals, unregister behavior on channel close, and live reflection of channel lag/out-of-sync/queue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java

Purpose: Marker `IOException` used when an `IPCLoggerChannel` has too many pending edit bytes and should be treated as unavailable for the current write.

Important APIs/types/functions: Empty package-private subclass of `IOException` with a stable `serialVersionUID`.

Control flow: `IPCLoggerChannel.reserveQueueSpace` throws this when queue limits would be exceeded while existing bytes are pending; `sendEdits` converts it to an immediate failed future so quorum handling can proceed.

State and persistence behavior: No state or persistence. It protects client memory by stopping further queuing for a slow logger.

Dependencies/integration: Consumed by `IPCLoggerChannel` and indirectly by `AsyncLoggerSet.waitForWriteQuorum`.

Risks: The exception carries no message, so diagnosis depends on the warning logged at the throw site. Treating the logger as failed relies on enough remaining loggers for quorum.

Test signals: Queue-limit tests should assert failed future type, warning path, and successful quorum writes with one lagging logger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java

Purpose: Tracks a set of asynchronous calls and waits until response, success, or failure thresholds are reached.

Important APIs/types/functions: `create`, `waitFor`, `cancelCalls`, `countResponses`, `countSuccesses`, `countExceptions`, `getResults`, `rethrowException`, `mapToString`, and internal pause detection via `StopWatch`/`Timer`.

Control flow: Factory registers direct-executor callbacks on every future; callbacks synchronize, store success or exception by key, and notify waiters. `waitFor` loops until response thresholds are met, periodically logs progress, detects possible process pauses and extends the deadline, and throws `TimeoutException` only after adjusted time expires.

State and persistence behavior: Keeps in-memory maps of successes and exceptions plus all futures for cancellation. Result maps are copied when returned, but the underlying call can still receive late completions.

Dependencies/integration: Used by `AsyncLoggerSet` and `QuorumJournalManager` for quorum RPCs. Exception messages include `RemoteException` assertion handling when Java assertions are enabled.

Risks: Direct callbacks execute on completing threads, so expensive callback work would be harmful; current callbacks are small. Timeout extension is heuristic and can mask long pauses. `maxExceptions` semantics return when count is greater than the threshold, matching majority-failure use but requiring care for callers.

Test signals: Tests should cover all wait exit conditions, late completion after return, cancellation, timeout logging thresholds, pause-based timeout increase with fake `Timer`, assertion-error rethrow, and `mapToString` protobuf formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java

Purpose: IOException used when a quorum operation receives too many failures to satisfy the required success threshold.

Important APIs/types/functions: Static factory `create(simpleMsg, successes, exceptions)` builds a diagnostic message including successes and per-logger failures.

Control flow: Callers pass accumulated result maps from `QuorumCall`; runtime exceptions are stringified with stack traces, checked exceptions prefer localized messages, and null successes are rendered explicitly.

State and persistence behavior: No persistent state. The created message is the primary state and is intended for operator/test diagnostics.

Dependencies/integration: Thrown by `QuorumCall.rethrowException` and `AsyncLoggerSet.waitForWriteQuorum`; uses Guava `Joiner`, Hadoop `StringUtils`, and `Preconditions`.

Risks: Message order follows map iteration order, which may be nondeterministic. Checked exceptions without useful messages still fall back to stack stringification.

Test signals: Verify empty-exception rejection, success and failure message formatting, runtime stack inclusion, checked-exception message handling, and stable behavior with null success values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumJournalManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumJournalManager.java

Purpose: HDFS `JournalManager` implementation that writes edit logs to a quorum of JournalNodes, coordinates fencing/recovery epochs, and selects edit-log input streams for readers and standby tailers.

Important APIs/types/functions: Constructors configure timeouts, RPC fetch limits, HTTP connection factory, and logger set. Key methods include `createLoggers`, `parseJournalId`, `createNewUniqueEpoch`, `recoverUnfinalizedSegments`, `recoverUnclosedSegment`, `startLogSegment`, `finalizeLogSegment`, `selectInputStreams`, `selectRpcInputStreams`, `selectStreamingInputStreams`, upgrade/rollback methods, `discardSegments`, and `getJournalCTime`.

Control flow: Active write startup obtains a quorum of journal states, picks `max(lastPromisedEpoch)+1`, calls `newEpoch`, then recovers the most recent unclosed segment. Recovery prepares all loggers, selects the best segment via `SegmentRecoveryComparator`, asks a quorum to accept the chosen state using an HTTP source URL, and finalizes the agreed length. Normal writes start a segment on a quorum and return `QuorumOutputStream`. Read selection first tries in-progress RPC tailing if enabled, otherwise falls back to HTTP streaming from manifests.

State and persistence behavior: Client-local state includes active-writer flag, output buffer capacity, timeout values, and HTTP connection resources. Durable effects are remote JournalNode epochs, edit segments, Paxos recovery files, and finalized logs. `setOutputBufferCapacity` guards against IPC payloads larger than configured max data length.

Dependencies/integration: Bridges NameNode edit logging (`JournalManager`, `JournalSet`, `EditLogInputStream/OutputStream`) with qjournal clients, `URLConnectionFactory`, DFS config keys, `LogThrottlingHelper`, protobuf recovery state, and `FileJournalManager`-style remote manifests.

Risks: Even JournalNode counts are warned but allowed. Recovery currently selects one best source URL, so failure of that source during accept recovery can reduce availability. RPC tailing depends on JournalNode cache coverage and falls back on failures. All-nodes operations for format/upgrade require every logger to respond, unlike normal quorum writes.

Test signals: Tests should cover URI validation, logger creation, epoch fencing, recovery tie-breaking, committed-txid invariant checks, start-before-recover rejection, IPC max data length validation, RPC tailing durable-count selection, streaming fallback, upgrade/rollback all-results-equal checks, and behavior with even/partial logger sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumJournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumOutputStream.java

Purpose: `EditLogOutputStream` that buffers NameNode edit operations and flushes batches to a quorum of remote JournalNodes.

Important APIs/types/functions: Constructor wires `AsyncLoggerSet`, segment txid, buffer capacity, write timeout, and log version. Overrides `write`, `writeRaw`, `setReadyToFlush`, `shouldForceSync`, `flushAndSync`, `generateReport`, `abort`, and `close`.

Control flow: Operations are written to an `EditsDoubleBuffer`. `setReadyToFlush` flips the buffer; `flushAndSync` copies ready bytes into a defensive `DataOutputBuffer`, sends them to all loggers, waits for write quorum, then advances committed txid on all channels after quorum success.

State and persistence behavior: Holds transient double-buffered edit bytes for one segment. Durability is achieved only after `waitForWriteQuorum` succeeds; committed txid propagation lets lagging JournalNodes know a quorum has fsynced the batch.

Dependencies/integration: Created by `QuorumJournalManager.startLogSegment`; depends on NameNode edit-log encoding (`FSEditLogOp`, `EditsDoubleBuffer`) and qjournal quorum fan-out.

Risks: `abort` nulls the buffer then calls `close`, which is safe because `close` checks null. The defensive byte copy is required because asynchronous RPCs outlive the mutable edit buffer; removing it would risk corrupt sends. The `durable` flush parameter is ignored because quorum write itself provides durability.

Test signals: Verify flush sends correct first txid/count/bytes, committed-txid update after success only, no-op flush on empty buffer, buffer close/abort behavior, force-sync threshold propagation from `EditsDoubleBuffer`, and report content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java

Purpose: Orders `prepareRecovery` responses to choose the safest segment state for recovery.

Important APIs/types/functions: Singleton `INSTANCE` implements `Comparator<Entry<AsyncLogger, PrepareRecoveryResponseProto>>`.

Control flow: Responses with segment state beat responses without a segment. Finalized segments beat in-progress segments. Finalized segments must have identical lengths or an assertion is thrown. In-progress segments are ordered by the highest seen epoch (`max(acceptedInEpoch,lastWriterEpoch)`) and then by larger end txid.

State and persistence behavior: No state. It interprets persisted JournalNode Paxos/recovery metadata and segment scan results supplied in protobuf responses.

Dependencies/integration: Used by `QuorumJournalManager.recoverUnclosedSegment`; depends on `PrepareRecoveryResponseProto`, `SegmentStateProto`, Guava `ComparisonChain`, and boolean comparison helpers.

Risks: Assumes it is only comparing responses for the same segment start txid. If finalized lengths differ, it fails hard because that violates qjournal safety invariants. It does not collect all equal best sources, so recovery uses a single selected logger URL.

Test signals: Cover no-segment comparisons, segment-vs-empty, finalized-vs-in-progress, differing finalized length assertion, accepted epoch precedence over length, last-writer epoch ordering, and equal start-txid precondition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java

Purpose: Defines JournalNode-to-JournalNode RPCs used by the optional journal syncer to discover and synchronize edit logs between peers.

Important APIs/types/functions: `getEditLogManifestFromJournal(jid, nameServiceId, sinceTxId, inProgressOk)` and `getStorageInfo(jid, nameServiceId)`. The interface has qjournal-specific Kerberos annotations and version id `1L`.

Control flow: A JournalNode sync client asks a peer for its manifest or storage identity; server implementations delegate into the same journal state used for NameNode-facing manifests.

State and persistence behavior: No state in the interface. Responses expose persisted edit-log manifests and storage metadata for a named journal.

Dependencies/integration: Implemented over protobuf by `InterQJournalProtocolPB` translators and served by JournalNode RPC plumbing. Uses JournalNode Kerberos principal for both client and server because both ends are JournalNodes.

Risks: Manifest correctness depends on peer storage consistency and nameservice selection. In-progress inclusion must be handled carefully so syncers do not copy unstable data incorrectly.

Test signals: Inter-JN RPC tests should verify manifest filtering by txid, storage info conversion, optional nameservice id handling, Kerberos annotation expectations, and behavior against unformatted or missing journals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java

Purpose: Signals that a JournalNode operation requiring formatted storage was invoked before the journal storage reached normal formatted state.

Important APIs/types/functions: Public constructor accepting a message; subclass of `IOException`.

Control flow: `Journal.checkFormatted` throws this for operations such as epoch negotiation, writes, manifests, and recovery when `JNStorage.isFormatted()` is false.

State and persistence behavior: No state beyond the message. It protects persistent storage from writes against uninitialized or unformatted directories.

Dependencies/integration: Propagates through `QJournalProtocol` translators as RPC failures and influences format/has-data flows in `QuorumJournalManager`.

Risks: Callers must distinguish this expected operational state from other IO failures. Message content includes local storage path and journal id, which is useful but should not be exposed beyond trusted admin channels.

Test signals: Tests should exercise unformatted journal responses for write, recovery, manifest, and state calls, and verify successful operations after format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java

Purpose: Signals that a JournalNode's local write state no longer matches the active writer's expected segment or transaction sequence.

Important APIs/types/functions: Public constructor accepting a message; subclass of `IOException`.

Control flow: Thrown by server-side `Journal.checkSync` and by client-side `IPCLoggerChannel.throwIfOutOfSync`. A failed write causes the channel to stop useful writes until the next segment roll.

State and persistence behavior: The exception itself has no state. It protects durable edit-log invariants such as contiguous txids, correct segment id, and no overwriting finalized segments.

Dependencies/integration: Propagates through qjournal RPCs; quorum logic can tolerate it from minority loggers while still committing to a majority.

Risks: Frequent out-of-sync failures indicate a logger is lagging or an ordering invariant broke. Recovery depends on subsequent log roll or segment recovery to restore participation.

Test signals: Tests should verify txid mismatch, segment mismatch, missing segment, and client out-of-sync heartbeat paths all surface this exception and preserve quorum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java

Purpose: NameNode-to-JournalNode RPC contract for quorum edit logging, recovery, reading, and storage lifecycle operations.

Important APIs/types/functions: Formatting/state calls (`isFormatted`, `getJournalState`, `format`, `newEpoch`), write calls (`journal`, `heartbeat`, `startLogSegment`, `finalizeLogSegment`, `purgeLogsOlderThan`), read calls (`getEditLogManifest`, `getJournaledEdits`), recovery calls (`prepareRecovery`, `acceptRecovery`), and upgrade/rollback/discard/ctime operations.

Control flow: Active NameNode obtains state, proposes a new epoch, recovers unfinalized segments, starts segments, journals batches with `RequestInfo`, finalizes segments, and may purge old logs. Standby/readers fetch manifests or RPC-cached edits. Recovery uses prepare/accept to converge a quorum on one segment length.

State and persistence behavior: Methods mutate or expose JournalNode storage: namespace format data, edit log files, in-progress/finalized segment names, persisted promised/writer epochs, committed txid, and Paxos recovery records.

Dependencies/integration: Consumed by `IPCLoggerChannel` through `QJournalProtocolTranslatorPB`; implemented by JournalNode RPC server delegation into `Journal`. Security annotations use JournalNode server principal and NameNode client principal.

Risks: Correctness relies on `RequestInfo` epoch and serial enforcement on the server. `getJournaledEdits` requires the in-memory JournalNode cache and can fail on cache misses, so callers need streaming fallback. Some admin operations require all JournalNodes, unlike quorum writes.

Test signals: Protocol tests should cover all translator conversions, optional nameservice ids, idempotent `discardSegments`, recovery handshakes, namespace consistency checks, cache-miss handling, and old-client layout-version defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java

Purpose: Value object attached to mutating qjournal RPCs to identify the journal, nameservice, active-writer epoch, per-epoch IPC serial, and highest committed transaction known by the writer.

Important APIs/types/functions: Constructor plus getters/setters for epoch and IPC serial, `getJournalId`, `getNameServiceId`, `getCommittedTxId`, and `hasCommittedTxId`.

Control flow: `IPCLoggerChannel.createReqInfo` increments the serial for each write-like RPC. `Journal.checkRequest` uses epoch to fence stale writers, serial to reject reordered/retried stale IPCs, and committed txid to update local lag/recovery metadata.

State and persistence behavior: In-memory RPC payload only. Its fields drive persistent updates to `last-promised-epoch` and `committed-txid` on the server.

Dependencies/integration: Converted to/from `RequestInfoProto` by `QJournalProtocolTranslatorPB` and server translator. Uses `HdfsServerConstants.INVALID_TXID` to represent absent committed txid.

Risks: Epoch and serial setters make the object mutable, so callers should not reuse it across RPCs after conversion. Moving committed txid backwards is rejected by server/client preconditions.

Test signals: Verify protobuf conversion with and without nameservice/committed txid, serial monotonic rejection, higher-epoch promise updates, and absent committed-txid behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java

Purpose: Protobuf RPC interface marker for `InterQJournalProtocol`, adding Hadoop protocol metadata and JournalNode Kerberos annotations to the generated blocking service.

Important APIs/types/functions: Extends `InterQJournalProtocolService.BlockingInterface`; annotated with `@ProtocolInfo` protocol name/version and `@KerberosInfo`.

Control flow: No executable logic. Hadoop RPC uses this interface to bind generated protobuf service methods to secure JournalNode-to-JournalNode RPC endpoints.

State and persistence behavior: None. It only declares the wire service contract.

Dependencies/integration: Used by `InterQJournalProtocolTranslatorPB`, server-side translator, and JournalNode RPC server setup.

Risks: Protocol name and version must remain compatible with clients. Kerberos principal choice must match inter-JournalNode authentication.

Test signals: RPC compatibility tests should verify `isMethodSupported`, protocol version negotiation, and secure client/server principal configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java

Purpose: Server-side protobuf adapter that converts `InterQJournalProtocolPB` requests into calls on an `InterQJournalProtocol` implementation.

Important APIs/types/functions: Constructor accepts the delegate. Implements `getEditLogManifestFromJournal` and `getStorageInfo`, translating journal id and optional nameservice id fields and wrapping `IOException` in `ServiceException`.

Control flow: Each RPC method extracts protobuf fields, calls the Java protocol delegate, and returns the delegate's protobuf response or storage info proto directly.

State and persistence behavior: No owned state beyond the delegate reference. Persistent effects are whatever the delegate's JournalNode implementation performs or exposes.

Dependencies/integration: Used by JournalNode RPC server for syncer APIs; shares `GetEditLogManifestRequestProto` with the main qjournal protocol.

Risks: Optional nameservice ids become null when absent, so delegate behavior must consistently select storage directories. All IO failures cross the RPC boundary as `ServiceException`.

Test signals: Verify request field conversion, absent nameservice handling, exception wrapping, and delegate invocation for manifest and storage info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java

Purpose: Client-side adapter that implements `InterQJournalProtocol` by building protobuf requests and invoking an `InterQJournalProtocolPB` proxy.

Important APIs/types/functions: `getEditLogManifestFromJournal`, `getStorageInfo`, `close`, `isMethodSupported`, and private `convertJournalId`.

Control flow: Methods build request protos, conditionally set `nameServiceId`, call the RPC proxy through shaded protobuf `ipc`, and return protobuf responses. `close` stops the proxy.

State and persistence behavior: Holds only the RPC proxy. It reads peer JournalNode state; no local persistence.

Dependencies/integration: Used by JournalNode syncer clients; integrates with Hadoop `RPC`, `RpcClientUtil`, and protobuf helper error translation.

Risks: Request construction must remain in sync with server optional-field names. Failure to close leaks RPC proxy resources.

Test signals: Verify protobuf construction, null nameservice omission, close behavior, method support probing, and IOException translation from `ServiceException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java

Purpose: Protobuf RPC interface marker for the main `QJournalProtocol`, adding protocol metadata and NameNode-to-JournalNode Kerberos annotations to the generated blocking service.

Important APIs/types/functions: Extends `QJournalProtocolService.BlockingInterface`; annotated with protocol name `org.apache.hadoop.hdfs.qjournal.protocol.QJournalProtocol`, version `1`, and qjournal Kerberos principals.

Control flow: No logic. Hadoop RPC binds generated protobuf qjournal service methods through this interface.

State and persistence behavior: None. It declares the wire service surface for remote JournalNode mutation and read operations.

Dependencies/integration: Used by `IPCLoggerChannel.createProxy`, `QJournalProtocolTranslatorPB`, and server-side translator registration.

Risks: Protocol metadata changes are compatibility-sensitive. Security annotations must align with NameNode client and JournalNode server login configuration.

Test signals: RPC setup tests should verify protocol engine registration, method support queries, secure principal resolution, and version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolServerSideTranslatorPB.java

Purpose: Server-side protobuf adapter from generated qjournal RPC methods to a Java `QJournalProtocol` implementation.

Important APIs/types/functions: Implements all qjournal RPC methods: formatting/state, epoch, journal/heartbeat, segment start/finalize/purge, manifests, RPC edits, recovery, upgrade/rollback, discard, and ctime. Helper `convert(RequestInfoProto)` reconstructs `RequestInfo`.

Control flow: Each method extracts protobuf fields, converts namespace/storage/request info as needed, delegates to `impl`, and returns default or populated response protos. `startLogSegment` defaults missing layout version to current NameNode layout for old clients. URL strings are converted for `acceptRecovery`.

State and persistence behavior: Owns only the protocol delegate. It passes mutation requests through to `Journal`, where edit logs, epoch files, committed txid, and recovery files are persisted.

Dependencies/integration: Used by JournalNode RPC server; depends on `PBHelper`, `NameNodeLayoutVersion`, `HdfsServerConstants.INVALID_TXID`, and qjournal protobuf types.

Risks: Optional field naming is inconsistent in rollback (`nameserviceId` vs `nameServiceId`), so translator tests matter. All `IOException`s are wrapped in `ServiceException`, requiring client-side unwrapping. Default layout version behavior is compatibility-sensitive.

Test signals: Full translator tests should round-trip every RPC, optional committed-txid/nameservice fields, default layout version, storage conversions, URL parsing, exception wrapping, and discard idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolTranslatorPB.java

Purpose: Client-side adapter that implements `QJournalProtocol` by building protobuf requests for a `QJournalProtocolPB` proxy.

Important APIs/types/functions: All Java protocol methods are implemented; important helpers are `convertJournalId`, `convert(RequestInfo)`, `close`, and `isMethodSupported`.

Control flow: Methods build request protos, conditionally add optional `nameServiceId` and `committedTxId`, convert namespace/storage data through `PBHelper`, wrap edit bytes with `PBHelperClient.getByteString`, invoke the RPC proxy via shaded `ipc`, and return converted response values.

State and persistence behavior: Holds only the RPC proxy. Durable state is changed on the remote JournalNode according to the invoked request.

Dependencies/integration: Used by `IPCLoggerChannel` as the concrete RPC proxy wrapper; integrates Hadoop RPC lifecycle, protocol metadata checks, and protobuf request/response types.

Risks: Because edit batches are copied into protobuf `ByteString`, large batches are bounded by IPC max data length and qjournal buffer settings. Inconsistent optional field names for rollback need compatibility tests. Missing close leaks the proxy.

Test signals: Verify request construction for every method, byte payload integrity, optional nameservice and committed-txid handling, storage conversions, `isMethodSupported`, close behavior, and RPC exception translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java

Purpose: HTTP servlet that serves local edit-log segment files to NameNodes and peer JournalNodes for streaming reads and recovery synchronization.

Important APIs/types/functions: `doGet`, `isValidRequestor`, `checkRequestorOrSendError`, `checkStorageInfoOrSendError`, and static `buildPath`. Query parameters are `jid`, `segmentTxId`, `storageInfo`, and `inProgressOk`.

Control flow: `doGet` reads configuration and query parameters, validates journal id, resolves the `Journal` from servlet context, checks security and namespace/cluster match, finds the requested edit file under synchronized `FileJournalManager`, sets transfer headers, opens the file, and streams it through `TransferFsImage` with optional throttling.

State and persistence behavior: It does not mutate journal state. It exposes finalized or in-progress edit-log files from `JNStorage` and protects against races with finalization by synchronizing on `FileJournalManager` while locating and opening the file.

Dependencies/integration: Registered by `JournalNodeHttpServer` at `/getJournal`; URLs are built by `IPCLoggerChannel`/`QuorumJournalManager`. Security integrates NameNode principals, SecondaryNameNode principal, and same-short-name JournalNode peer access.

Risks: Any thrown `Throwable` becomes an HTTP 500 and IOException; security fallback for peer JournalNodes uses short username matching because peer principals are not enumerated. Storage info is optional, so callers omitting it bypass namespace/cluster comparison.

Test signals: Servlet tests should cover allowed/rejected principals, namespace mismatch 403, missing segment 404, in-progress flag behavior, path URL encoding, transfer headers, throttling, and race behavior around finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java

Purpose: JournalNode-specific `Storage` wrapper around a single journal directory and `FileJournalManager`.

Important APIs/types/functions: Constructor analyzes/recovers storage. Key methods include `format`, `analyzeStorage`, `refreshStorage`, `checkConsistentNamespace`, `findFinalizedEditsFile`, edit-file path builders, Paxos path builders, `purgeDataOlderThan`, `getOrCreatePaxosDir`, upgrade-related storage overrides, `isFormatted`, and `close`.

Control flow: Startup creates a `StorageDirectory`, `FileJournalManager`, and analyzes state. Format clears the directory, writes namespace properties, creates `paxos`, and re-analyzes. Purge removes old edit logs through FJM and old numeric Paxos decision files. Recovery startup delegates abnormal storage states to `StorageDirectory.doRecover`.

State and persistence behavior: Persists VERSION/properties, finalized and in-progress edit files under `current`, Paxos recovery decisions under `current/paxos`, sync temporary files, and journal-sync staging under `edits.sync`. Layout version checks are relaxed because JournalNodes mostly scan edit files rather than decode all future layouts.

Dependencies/integration: Owned by `Journal`; uses HDFS `Storage`, `NNStorage` edit-file naming, `FileJournalManager`, and configured journal directory permissions.

Risks: `getOrCreatePaxosDir` logs but does not throw if `mkdir` fails, so later file creation reveals the error. Purge deletes numeric Paxos files by txid and assumes no unrelated numeric files live there. Layout version relaxation must stay compatible with edit-log scanning behavior.

Test signals: Cover format/force semantics, namespace consistency failures, path generation, paxos purge, startup recovery states, rollback/upgrade storage refresh, directory permission creation, and missing finalized-file errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/Journal.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/Journal.java

Purpose: Core per-journal server implementation. It enforces qjournal fencing/order invariants, writes edit batches to local files, maintains tailing cache/metrics, and implements Paxos-like recovery for unfinalized segments.

Important APIs/types/functions: Lifecycle/state methods `format`, `close`, `newEpoch`, `journal`, `heartbeat`, `startLogSegment`, `finalizeLogSegment`, `purgeLogsOlderThan`, `getEditLogManifest`, `getJournaledEdits`, `prepareRecovery`, `acceptRecovery`, `syncLog`, `persistPaxosData`, `completeHalfDoneAcceptRecovery`, upgrade/rollback methods, `discardSegments`, and `moveTmpSegmentToCurrent`.

Control flow: On construction, storage is analyzed, epoch/committed files are opened, optional `JournaledEditsCache` is created, and latest edits are scanned. `newEpoch` verifies namespace, persists a higher promised epoch, aborts current segment, and reports latest segment. `journal` checks epoch/serial/writer epoch, validates contiguous txids, caches bytes, writes and flushes to the current segment, optionally skipping fsync for already committed lagging edits, then advances highest txid. Recovery prepare aborts current writes, rolls forward half-done accepts, reports accepted or on-disk segment state, writer epoch, and committed txid. Accept recovery may download a chosen segment to a temp file, atomically persist Paxos data, then replace the in-progress edit file.

State and persistence behavior: Persistent files include edit segments, `last-promised-epoch`, `last-writer-epoch`, best-effort `committed-txid`, and `paxos/<segmentTxId>` records containing delimited protobuf plus debug text. Runtime state tracks current output stream, segment txid/layout, next txid, highest written txid, current epoch IPC serial, cache, and last journal timestamp.

Dependencies/integration: Called by JournalNode RPC server through `QJournalProtocol`; uses `JNStorage`, `FileJournalManager`, `JournaledEditsCache`, `TransferFsImage`, `AtomicFileOutputStream`, `PersistentLongFile`, `BestEffortLongFile`, metrics, and security login for recovery downloads.

Risks: Correctness depends on synchronized methods and strict IPC serial monotonicity. `acceptRecovery` intentionally spans download plus Paxos persistence; fault injection tests are required to validate roll-forward semantics. Cache-based RPC tailing can miss requested edits and must fail cleanly. Skipping fsync for lagging edits relies on committed-txid being a safe lower bound from a quorum.

Test signals: Critical tests include epoch fencing, stale/reordered IPC rejection, txid continuity, segment mismatch out-of-sync abort, start-log overwrite guards, finalize validation, Paxos persistence fault injection, half-done recovery roll-forward, committed-txid monotonicity, RPC cache hit/miss/newer-txid paths, purge/discard behavior, and upgrade/rollback copying of epoch files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/Journal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java

Purpose: Test hook for injecting failures around Paxos recovery persistence in `Journal.acceptRecovery`.

Important APIs/types/functions: Static mutable `instance`, `get`, `beforePersistPaxosData`, and `afterPersistPaxosData`.

Control flow: Production methods are no-ops. Tests replace `instance` to throw before or after `persistPaxosData`, exercising the recovery operation's atomicity and roll-forward behavior.

State and persistence behavior: No production persistence. It targets the boundary between downloaded temporary edit files and persisted Paxos decision files.

Dependencies/integration: Called only by `Journal.acceptRecovery`; marked visible for testing and private audience.

Risks: Static global replacement can leak between tests if not reset. Production code assumes no-op behavior and does not guard against injected exceptions except through normal IO failure paths.

Test signals: Fault-injection tests should reset the singleton, fail before/after Paxos persistence, restart/reprepare the journal, and verify no externally visible partial recovery or data loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java

Purpose: Server-side Hadoop metrics source for one `Journal`.

Important APIs/types/functions: Counters for batches, txns, bytes written, RPC-served txns/bytes, empty RPC responses, lagging batches, and synced edit logs; quantiles for sync latency; stat `RpcRequestCacheMissAmount`; metric getters for journal id, writer/promised epochs, highest txid, lag txns, and last journal timestamp.

Control flow: `create` registers a metrics source named `Journal-<journalId>`. `Journal` increments counters and adds sync latencies during writes, RPC tailing, cache misses, and syncer activity. Getter methods tolerate epoch-read IO failures by returning `-1`.

State and persistence behavior: Metrics are in-memory only and derived from `Journal` persistent/runtime state.

Dependencies/integration: Used by `Journal`; registered with `DefaultMetricsSystem`; consumed by Hadoop metrics sinks and JMX.

Risks: Metrics source names collide for duplicate journal ids in one JVM. Getter IO failures are hidden as `-1`, so dashboards must interpret that as unavailable/error.

Test signals: Verify counter increments on journal writes, lagging writes, RPC cache responses/misses, syncer increments, quantile updates, source naming, and fallback values when epoch files throw IO errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java

Purpose: Daemon wrapper that hosts qjournal RPC/HTTP servers and manages multiple per-journal `Journal` instances in one JVM.

Important APIs/types/functions: `setConf`, `start`, `stop`, `join`, `getOrCreateJournal`, `startSyncer`, `getLogDir`, MXBean methods, upgrade/rollback/discard/ctime delegators, HTTP/RPC address accessors, and `main`.

Control flow: Configuration resolves local journal directories, including nameservice-specific paths. Startup validates directories, initializes metrics and security login, registers MXBean, starts HTTP server, then RPC server. `getOrCreateJournal` validates journal id, constructs `Journal` lazily, and starts optional `JournalNodeSyncer`. Stop shuts down syncers, RPC, HTTP, journals, metrics, MXBean, and tracer.

State and persistence behavior: Runtime maps track journals and syncers by journal id. Persistent state belongs to each `Journal` directory under configured edits dirs. MXBean status infers formatted journals from loaded journals and on-disk directories.

Dependencies/integration: Implements `Tool`, `Configurable`, and `JournalNodeMXBean`; integrates with `JournalNodeRpcServer`, `JournalNodeHttpServer`, security, metrics, tracing, disk checks, and DFS config keys.

Risks: Federated nameservice directory resolution is configuration-sensitive. MXBean may mark any directory under a journal dir as formatted even if not analyzed. ErrorReporter stops the daemon on storage file errors. Lazy journal creation means first RPC can trigger storage analysis and syncer startup.

Test signals: Tests should cover startup/shutdown, absolute directory validation, HA/federated directory selection, lazy journal creation, syncer enablement and retry flags, MXBean JSON/status, security login address, error reporter stop, and upgrade delegator paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java

Purpose: Encapsulates the JournalNode HTTP/HTTPS server used for edit-log transfer and web servlet context.

Important APIs/types/functions: Constructor, `start`, `stop`, `getAddress`, `getHttpAddress`, `getHttpsAddress`, `getServerURI`, static `getJournalFromContext`, and `getConfFromContext`.

Control flow: Startup builds an `HttpServer2` from DFS HTTP policy, HTTP bind address, HTTPS address/bind-host overrides, SPNEGO principal/keytab, and X-Frame settings. It stores the local `JournalNode` and configuration in the servlet context, registers `/getJournal`, starts the server, and records actual bound connector addresses back into configuration.

State and persistence behavior: No durable state. Runtime state is HTTP server instance and bound connector addresses. It exposes access to persistent journal files through servlet lookup.

Dependencies/integration: Owned by `JournalNode`; registers `GetJournalEditServlet`; uses `DFSUtil.getHttpServerTemplate`, `HttpConfig.Policy`, `NetUtils`, `JspHelper`, and qjournal HTTP config keys.

Risks: Connector index assumptions depend on DFS HTTP policy ordering. `getAddress` asserts at least one connector is present. The servlet context lookup creates journals lazily when HTTP fetches reference a journal id.

Test signals: Verify HTTP-only, HTTPS-only, and dual policies; bind-host overrides; config update with actual ports; servlet registration and context attributes; server URI scheme; and clean stop error wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java -->
