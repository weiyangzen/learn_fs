# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournalSystem.java

## Purpose
`NoopJournalSystem` is a complete journal-system implementation with no persistence or replay behavior.

## Important APIs, Types, And Functions
`createJournal` returns `NoopJournal`; lifecycle, primacy, suspend/resume, format, checkpoint, and sink operations are no-ops. `catchup` returns a completed future. `getCurrentSequenceNumbers` and sink lookups return empty collections. `isFormatted` and `isEmpty` return true.

## Control Flow, State, Dependencies, Risks, And Tests
There is no state and no persisted journal data. It is selected by `JournalSystem.Builder` for `JournalType.NOOP`. Dependencies include `JournalSystem`, `NoopJournal`, and `CatchupFuture`. Risks are severe data loss if selected accidentally, and lack of sink callbacks even if sinks are added. Tests should cover all interface methods, builder selection, completed catch-up, formatted/empty semantics, and ensuring production defaults do not select NOOP.
