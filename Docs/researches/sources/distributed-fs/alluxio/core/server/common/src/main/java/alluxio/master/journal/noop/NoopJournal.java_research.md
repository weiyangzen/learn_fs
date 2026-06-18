# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/noop/NoopJournal.java

## Purpose
`NoopJournal` is a `Journal` implementation that discards all writes.

## Important APIs, Types, And Functions
`getLocation` returns URI `/noop`, `createJournalContext` returns `NoopJournalContext.INSTANCE`, and `close` does nothing.

## Control Flow, State, Dependencies, Risks, And Tests
There is no mutable state or persistence. It integrates with `NoopJournalSystem` and test/formatting contexts. Dependencies include URI parsing and `NoopJournalContext`. Risks include accidental use in production configuration causing complete journal loss, and `/noop` being a synthetic location. Tests should verify returned context, no-op close, URI value, and explicit configuration gating.
