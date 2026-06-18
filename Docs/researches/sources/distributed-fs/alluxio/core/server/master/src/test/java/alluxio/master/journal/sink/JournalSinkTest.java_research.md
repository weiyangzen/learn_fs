# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/sink/JournalSinkTest.java

Purpose: integration tests for `JournalSink` delivery from the file-system master during live journal writes, replay, restart, and standby tailing.

Important APIs/types/functions: uses `JournalSystem`, `JournalSink`, `MasterRegistry`, `CoreMasterContext`, `MetricsMasterFactory`, `BlockMasterFactory`, `FileSystemMasterFactory`, `FileSystemMaster`, and file operation contexts for create, complete, rename, and delete. `TestJournalSink` appends entries to both a queue used by find helpers and an all-entry list used for replay comparison.

Control flow: setup configures UFS journaling, short tailer sleep, NOSASL auth, test work/root UFS directories, creates a journal system, registers a sink for the file-system master, starts masters as leader, and obtains `FileSystemMaster`. `writeEvents` performs file/dir create, nested create, rename, file delete, and recursive directory delete, then polls sink entries for expected inode, rename, and delete records. `writeInodePaths` repeats the mutation set while asserting path fields on inode, update, rename, and delete journal entries. `replayEvents` starts a standby with its own sink, generates 5000 random create/rename/delete operations, restarts the leader with a new sink, waits for leader-replay and standby counts to match the original sink, strips sequence numbers, and compares journal content.

State and persistence behavior: exercises UFS-backed journal files through master restart and standby replay. The sink itself is in-memory, but observations come from real journal emission and tailing.

Dependencies and integration points: depends on Alluxio master registry startup order, file-system master journaling, journal sink registration/removal, test UFS directories, and randomized operation generation.

Risks: queue polling consumes entries and makes helper order important. Random replay workload can make failures harder to reproduce. The standby registry created in `replayEvents` is not held for explicit stop in the test body, relying on process/test cleanup.

Test signals: strong integration signal that sink callbacks see semantically rich file-system journal entries during writes and replay, including path propagation.
