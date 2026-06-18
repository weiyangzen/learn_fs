# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/NoopRaftJournalSystem.java

## Purpose
`NoopRaftJournalSystem` is a lightweight raft journal test double with controllable leadership and no external raft side effects.

## Important APIs, Types, and Functions
It extends `RaftJournalSystem`, exposes `setIsLeader`, overrides `start`, `stop`, `isLeader`, `startInternal`, `stopInternal`, `gainPrimacy`, `losePrimacy`, and `createJournal`.

## Control Flow, State, and Persistence
Lifecycle methods are no-ops. `isLeader` returns the synchronized `mIsLeader` flag. `createJournal` returns a `NoopJournal`.

## Dependencies and Integration Points
The class depends on `RaftJournalSystem`, `NoopJournal`, `Master`, and master raft service addressing. It lets tests satisfy raft journal type dependencies without starting a real raft cluster.

## Risks
Because primacy methods do nothing, tests using this double must explicitly set leadership if behavior depends on it. It cannot validate persistence, quorum, or log replication.

## Test Signals
The double supports tests that only need journal-system shape, leadership state, and no-op journals.
