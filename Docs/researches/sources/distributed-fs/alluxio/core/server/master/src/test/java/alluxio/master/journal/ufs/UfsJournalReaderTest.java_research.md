# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalReaderTest.java

Purpose: tests `UfsJournalReader` state transitions and sequence tracking across checkpoints, completed logs, incomplete logs, and newly created logs.

Important APIs/types/functions: uses `JournalReader.State` (`CHECKPOINT`, `LOG`, `DONE`), `UfsJournal.getReader`, direct `UfsJournalReader` construction with a starting sequence number, `UfsJournalCheckpointWriter`, `CheckpointOutputStream`, `CheckpointType.JOURNAL_ENTRY`, and `UfsJournalLogWriter`.

Control flow: `readCheckpoint` writes a checkpoint payload, reads until `DONE`, and verifies the checkpoint stream bytes and next sequence number. `readCompletedLog` creates contiguous completed logs and verifies all entries in order and repeated `DONE`. `readIncompleteLogPrimary` confirms a primary reader consumes the current incomplete log, while `readIncompleteLogSecondary` confirms a secondary reader stops before it. `readNewLogs` reaches `DONE`, then creates new completed and incomplete logs and verifies the same reader can continue. Checkpoint-plus-log tests cover checkpoint end sequences that do or do not exactly match log boundaries. Resume tests start reading from within or after a checkpoint and still reach the final log end.

State and persistence behavior: durable state is checkpoint files and completed/current log files under the test UFS journal. Reader state tracks next sequence number and current state.

Dependencies and integration points: depends on file naming/snapshot discovery, checkpoint stream format, UFS flush support, and primary-vs-secondary semantics for incomplete logs.

Risks: malformed or corrupted entries are not covered here. Timing/tailing behavior is simplified by building logs synchronously.

Test signals: strong signal for reader ordering, checkpoint skipping/resume logic, and primary-only visibility of incomplete logs.
