# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/CountingNoopFileSystemMaster.java

## Purpose
`CountingNoopFileSystemMaster` is a test double for a file-system master that counts applied journal entries and can simulate slow or failing journal application.

## Important APIs, Types, and Functions
It extends `NoopMaster`, overrides `processJournalEntry`, `resetState`, and `getName`, exposes `setApplyDelay`, `getApplyCount`, and static factory `withApplyDelay`, and defines `ENTRY_DOES_NOT_EXIST`.

## Control Flow, State, and Persistence
On each journal entry, it optionally sleeps, increments `mApplyCount`, throws `NoSuchElementException` for delete-file entries, and otherwise returns true. `resetState` clears the count.

## Dependencies and Integration Points
It depends on `Journal.JournalEntry` and the `NoopMaster` lifecycle. Returning `"FileSystemMaster"` as the name ensures journal routing accepts test entries for file-system master journals.

## Risks
The class intentionally throws on a specific journal entry type, so tests using arbitrary delete-file entries can fail unexpectedly. The artificial delay preserves thread interrupt status but otherwise ignores exceptions.

## Test Signals
The double supports journal replay, apply-count, delay, and failure-path tests elsewhere in the journal suite.
