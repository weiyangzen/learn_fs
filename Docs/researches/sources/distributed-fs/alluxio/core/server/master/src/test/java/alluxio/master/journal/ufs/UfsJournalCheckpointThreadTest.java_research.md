# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalCheckpointThreadTest.java

Purpose: tests standby/checkpoint thread catch-up state, shutdown behavior, and checkpoint creation for UFS journals.

Important APIs/types/functions: uses `UfsJournal`, `UfsJournalCheckpointThread`, `UfsJournalSnapshot`, `UfsJournalLogWriter`, `MockMaster`, `NoopMaster`, `UnderFileSystem`, and `CloseableIterator`. Helpers build completed logs and then rename them to incomplete logs by using `UfsJournalFile.encodeLogFileLocation`.

Control flow: setup creates a spied UFS-backed journal for `FileSystemMaster`, starts it, and gains primacy. `catchupState` sets checkpoint period and tailer sleep, creates completed and incomplete logs, starts a checkpoint thread, waits until catch-up state is `DONE`, terminates it, and expects next sequence number 10. `catchStateShutdown` starts the thread then immediately awaits termination and expects `DONE`. `checkpointBeforeShutdown` sets a low checkpoint period and waits for a checkpoint ending at sequence 10 before shutdown. `checkpointAfterShutdown` shuts down after replay and verifies the mock master processed all ten completed log entries even if checkpointing was not required.

State and persistence behavior: UFS log/checkpoint files are the durable state. Incomplete current logs are present but standby checkpointing focuses on completed entries.

Dependencies and integration points: depends on UFS flush support mocking, journal snapshot discovery, configuration-driven checkpoint period, and mock master journal application.

Risks: timing waits can be sensitive to scheduler delays. The tests use empty lost-file sets and simple sequence-only entries, so richer master replay behavior is outside scope.

Test signals: good coverage that checkpoint threads converge to `DONE`, replay completed logs, and checkpoint before or during shutdown as expected.
