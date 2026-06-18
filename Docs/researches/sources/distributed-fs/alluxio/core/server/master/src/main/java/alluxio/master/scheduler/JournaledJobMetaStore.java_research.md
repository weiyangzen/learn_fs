# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/JournaledJobMetaStore.java

Purpose: journal-backed metadata store for scheduler jobs. It persists job state changes through the filesystem master's journal and reconstructs jobs from scheduler checkpoint/journal entries.

Important APIs/types/functions: implements `JobMetaStore` and `Journaled`; `getJournalEntryIterator`, `processJournalEntry`, `resetState`, `getCheckpointName`, `updateJob`, and `getJobs`.

Control flow: on journal replay, only entries with `loadJob` are accepted; the entry is passed to `JobFactoryProducer.create(entry, mFileSystemMaster).create()` and the resulting job is added to `mExistingJobs`. `updateJob` opens a `JournalContext` from `FileSystemMaster`, appends `job.toJournalEntry()`, then stores the job in the concurrent set.

State and persistence: live state is `ConcurrentHashSet<Job<?>> mExistingJobs`. Persistence is append-only through the file-system master's journal context and checkpoint name `SCHEDULER`. `resetState` clears only the in-memory set.

Dependencies/integration: integrates with scheduler `JobMetaStore`, Alluxio journal replay/checkpoint framework, `JobFactoryProducer`, and `FileSystemMaster` for journal context creation.

Risks: set identity/equality semantics depend on `Job` implementations. `getJobs` returns the live concurrent set, allowing callers to observe mutations. `updateJob` turns `UnavailableException` into a user-facing runtime message about backups, so backup/journal unavailability blocks scheduling persistence.

Test signals: replay accepted/rejected entries, checkpoint iterator content, update appending behavior, unavailable journal handling, reset behavior, and duplicate/equivalent job entries.
