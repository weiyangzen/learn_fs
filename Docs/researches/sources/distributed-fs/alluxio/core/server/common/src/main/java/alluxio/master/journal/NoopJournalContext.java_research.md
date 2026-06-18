# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/NoopJournalContext.java

## Purpose
`NoopJournalContext` is a singleton journal context that discards all entries.

## Important APIs, Types, And Functions
`INSTANCE` is the singleton. `append`, `flush`, and `close` are no-ops.

## Control Flow, State, Dependencies, Risks, And Tests
There is no state or persistence. It is used by noop journal implementations and test paths. Dependency is the `JournalContext` interface. Risks include accidentally using it in production paths and silently losing journal entries. Tests should assert singleton behavior, no exceptions on repeated close/flush, and that noop journal systems are only selected under explicit NOOP/test configuration.
