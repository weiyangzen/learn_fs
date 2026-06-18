# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journaled.java

## Purpose
`Journaled` defines the contract for components whose state can be replayed from journal entries and checkpointed.

## Important APIs, Types, And Functions
Implementations provide `processJournalEntry` and `resetState`. Default `applyAndJournal` mutates state then appends the entry. Default checkpoint methods write and restore journal-entry checkpoints via `JournalUtils`.

## Control Flow, State, Dependencies, Risks, And Tests
The intended mutation path is process in memory first, then append to the provided journal context. Persistent state is journal entries and checkpoints generated from `getJournalEntryIterator`. Dependencies include `Checkpointed`, `JournalEntryIterable`, and `JournalContext`. Risks include mutating memory before append failure, unsupported entries returning false but callers ignoring it, and checkpoint iterators not representing all state. Tests should cover replay idempotence, apply-and-journal ordering, append failure effects, reset behavior, and checkpoint round trips.
