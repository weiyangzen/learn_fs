# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournaled.java

## Purpose
`NoopJournaled` supplies default no-op implementations for journaled components.

## Important APIs, Types, And Functions
It accepts all journal entries, resets nothing, reports checkpoint name `NOOP`, writes an empty `JOURNAL_ENTRY` checkpoint header, restores no state, and returns an empty closeable iterator.

## Control Flow, State, Dependencies, Risks, And Tests
No state is persisted beyond an empty checkpoint type marker. Dependencies include checkpoint streams/types and `CloseableIterator`. Risks include `processJournalEntry` returning true for every entry, which can mask routing errors if used in a group, and empty checkpoints being mistaken for valid state. Tests should cover empty checkpoint header, empty iterator, default restore, and interactions with `JournaledGroup` ordering.
