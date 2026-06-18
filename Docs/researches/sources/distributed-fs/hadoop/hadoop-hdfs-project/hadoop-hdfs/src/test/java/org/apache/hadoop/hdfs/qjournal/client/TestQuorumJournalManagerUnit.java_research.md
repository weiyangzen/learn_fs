# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManagerUnit.java

Purpose: Pure Mockito unit tests for `QuorumJournalManager` quorum thresholds, output stream behavior, edit batching, auto-sync, and RPC-based edit stream selection.

Important APIs/types/functions: `futureReturns`, `futureThrows`, `createLogSegment`, `QuorumOutputStream`, `FSEditLog`, `selectInputStreams`, `getJournaledEdits`, `GetJournaledEditsResponseProto`, `EditLogFileOutputStream.writeHeader`, and `QJMTestUtil`.

Control flow: Setup creates three mock `AsyncLogger`s, stubs journal state, epoch, and format calls, then recovers. Tests exercise all-success, quorum-success, and quorum-failure starts; flush batching with exact txid ranges; output report formatting; buffer size rejection; FSEditLog auto-sync with a low buffer; slow logger writes; and RPC reads with identical, mismatched, slow, failed, or empty responses.

State and persistence behavior: No disk state. Edit-log bytes are synthesized in memory with valid headers and transaction payloads. Futures model asynchronous JN replies.

Dependencies and integration points: Exercises QJM logic around `AsyncLogger`, `QuorumOutputStream`, HDFS `FSEditLog`, and edit-log serialization.

Risks: Mock tests can miss real IPC/storage behavior, but they give fast coverage of quorum math and batching. Incorrect buffer behavior can break NameNode auto-sync.

Test signals: Passing shows quorum semantics, plain-text reports, correct send ranges, capacity validation, auto-sync, committed-txid propagation, and robust RPC tailing.
