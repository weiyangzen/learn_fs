# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JournalLoadJobFactory.java

## Purpose
`JournalLoadJobFactory` reconstructs a `LoadJob` from a persisted `LoadJobEntry` journal record during scheduler recovery.

## Important APIs, types, and functions
The constructor captures the journal entry and `FileSystemMaster`. `create()` extracts optional user, bandwidth, partial listing, verify flag, job id, load path, state, and optional end time; builds a `FileIterable` with `LoadJob.QUALIFIED_FILE_FILTER`; creates `LoadJob`; restores state and end time.

## Control flow
Creation is linear. The factory reconstructs listing behavior from persisted options and then applies persisted scheduler state after object construction.

## State and persistence behavior
It is a recovery adapter: only fields present in `LoadJob.toJournalEntry()` can be restored. Runtime counters, retry queues, failed-file maps, and iterators are not recovered; a running job resumes from a fresh iterator.

## Dependencies and integration points
It depends on journal proto `Job.LoadJobEntry`, `FileSystemMaster`, `FileIterable`, `LoadJob`, and `JobState.fromProto`. Scheduler journal replay uses this factory through `JobFactoryProducer`.

## Risks
Restored running jobs may repeat work because runtime progress is not journaled. If file-system state changes between original submission and replay, the new iterator sees current metadata. Invalid or obsolete job state proto values depend on `JobState.fromProto` behavior.

## Test signals
Tests should verify all optional fields, state restoration, end-time restoration, filter use, partial listing propagation, and replay behavior for completed versus running jobs.
