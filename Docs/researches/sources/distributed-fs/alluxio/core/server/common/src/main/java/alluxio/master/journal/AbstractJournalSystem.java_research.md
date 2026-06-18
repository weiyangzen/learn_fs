# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalSystem.java

## Purpose
`AbstractJournalSystem` provides lifecycle and journal-sink management for concrete journal systems.

## Important APIs, Types, And Functions
`start`/`stop` guard running state and call `startInternal`/`stopInternal`. Sink APIs add, remove, and retrieve `JournalSink`s per master or globally under a read/write lock. `registerMetrics` registers per-master sequence-number gauges.

## Control Flow, State, Dependencies, Risks, And Tests
The class tracks runtime running state and sink associations; persistence is owned by concrete UFS or Raft systems. On stop, all sinks receive `beforeShutdown` before `stopInternal`. Dependencies include `JournalSystem`, `Master`, `JournalSink`, `MetricsSystem`, and concurrent collections. Risks include returning mutable sink sets, sink callbacks under lifecycle transitions, metrics lambdas repeatedly calling `getCurrentSequenceNumbers`, and `stop` requiring running state. Tests should cover lifecycle preconditions, sink add/remove sharing, global sink recomputation, and metric registration.
