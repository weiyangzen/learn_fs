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
