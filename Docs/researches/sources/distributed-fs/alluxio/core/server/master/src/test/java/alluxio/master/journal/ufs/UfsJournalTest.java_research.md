# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalTest.java

Purpose: integration tests for the UFS journal lifecycle: formatting, availability, suspend/catch-up/resume, replay, standby catch-up, primacy transitions, and corrupted entry propagation.

Important APIs/types/functions: uses `UfsJournal`, `CountingNoopFileSystemMaster`, `CatchupFuture`, `UfsJournalLogWriter`, `UfsJournalCheckpointThread.CatchupState`, `UfsJournalSnapshot`, and journal protobuf entries.

Control flow: `format` creates checkpoint, temp checkpoint, completed logs, current log, and malformed files, then formats and expects all recognized journal artifacts gone. `unavailableAfterClose` verifies `createJournalContext` fails after close. `suspendNotAllowedOnPrimary` prevents suspending a primary. `suspendCatchupResume` uses a primary and standby sharing the same journal base, writes entries, suspends standby, catches up only to sequence 1, closes primary to complete the current log, then resumes standby to apply all entries. Replay tests verify initial startup catch-up and standby catch-up after losing primacy. Primacy tests cover gaining primary after suspend, after partial catch-up, and during in-progress catch-up. `subsequentCatchups` validates multiple target advances. `catchupCorruptedEntry` writes a bad delete entry and verifies `waitTermination` surfaces the apply error.

State and persistence behavior: durable UFS files are shared between primary and standby journals. Catch-up state transitions to `DONE`, sequence application counts model master state, and current logs are completed on primary close.

Dependencies and integration points: exercises UFS journal, checkpoint thread, file naming, standby reader, master apply errors, and primary lifecycle.

Risks: single-process primary/standby sharing a local path is simpler than distributed UFS deployment. Waits depend on background catch-up timing.

Test signals: strong behavioral coverage for UFS journal failover and backup-mode semantics.
