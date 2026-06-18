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
