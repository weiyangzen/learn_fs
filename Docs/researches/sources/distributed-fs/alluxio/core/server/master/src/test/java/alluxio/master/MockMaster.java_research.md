# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MockMaster.java

Purpose: minimal fake `Master` implementation for journal tests.

Important APIs/types/functions: constructor initializes an entry queue; `processJournalEntry` enqueues entries and returns true; `getJournalEntryIterator` returns a closeable iterator over queued entries; `createJournalContext` throws; other lifecycle/service/dependency methods are no-ops or null; `getCheckpointName` returns `NOOP`.

Control flow: journal replay or writer tests can hand entries to the fake master and later iterate them. It cannot create new journal contexts, so it is read/replay oriented.

State and persistence: in-memory `ArrayDeque<JournalEntry>`. No real persistence.

Dependencies/integration: implements `Master` and is used in UFS journal corruption setup where a journal object needs a master target.

Risks: methods returning null can break code expecting non-null master services/dependencies/context. Not thread-safe.

Test signals: use only where a simple journal receiver is sufficient; avoid for lifecycle tests requiring real master context.
