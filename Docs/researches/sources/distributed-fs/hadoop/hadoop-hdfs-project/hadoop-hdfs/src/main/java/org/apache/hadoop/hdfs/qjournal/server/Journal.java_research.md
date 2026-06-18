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
