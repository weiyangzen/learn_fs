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
