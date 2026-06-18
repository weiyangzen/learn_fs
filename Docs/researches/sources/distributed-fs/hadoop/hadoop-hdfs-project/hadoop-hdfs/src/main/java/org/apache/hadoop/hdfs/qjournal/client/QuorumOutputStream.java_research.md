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
