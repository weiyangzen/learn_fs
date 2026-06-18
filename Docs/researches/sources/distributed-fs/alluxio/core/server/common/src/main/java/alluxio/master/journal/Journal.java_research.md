# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/Journal.java

## Purpose
`Journal` is the per-master persistence handle for appending journal entries.

## Important APIs, Types, And Functions
It extends `Closeable`, exposes `getLocation`, and creates `JournalContext`s with `createJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
Concrete implementations enforce whether writes are allowed based on journal system mode and whether the journal is closed. Persistent state is the backend log at the returned URI. Dependencies are `JournalContext`, `UnavailableException`, and `URI`. Risks include contexts outliving closed journals, unclear location semantics for embedded journals, and caller misuse outside primary mode. Tests should target concrete journal implementations for context creation, close behavior, location values, and unavailable error mapping.
