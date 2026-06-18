# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/Journal.java

## Purpose
`Journal` is the legacy read-only journal abstraction. It gives callers a location, reader, and formatted-state check while intentionally not exposing a writer.

## Important APIs, Types, and Functions
The interface defines `getLocation()`, `getReader()`, and `isFormatted()`. The nested `Journal.Factory` implements `JournalFactory`, appends names to a base URI, and creates `UfsJournal` instances. `Factory.create(URI)` builds a read-only UFS journal for a concrete location.

## Control Flow, State, and Persistence
The interface has no state. The nested factory stores only `mBase`; each `create(String)` appends the requested name and converts URI syntax failures to runtime exceptions. All persistence and replay behavior is supplied by the `UfsJournal` implementation returned by the factory.

## Dependencies and Integration Points
It depends on `alluxio.master.journalv0.ufs.UfsJournal`, `JournalReader`, `JournalFactory`, and `URIUtils`. It is the read side of the legacy journal stack and is extended by `MutableJournal` for read-write use.

## Risks and Test Signals
Risks are mostly URI handling and accidental use where a mutable journal is required. Test signals include factory path construction, `isFormatted()` delegation, and reader behavior against formatted and unformatted UFS journal directories.
