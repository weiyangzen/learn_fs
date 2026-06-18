# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalWriter.java

## Purpose
`JournalWriter` is the low-level interface for writing and flushing journal entries.

## Important APIs, Types, And Functions
It extends `Closeable`, declares `write(JournalEntry)` and `flush`, both able to throw `IOException` or `JournalClosedException`.

## Control Flow, State, Dependencies, Risks, And Tests
`AsyncJournalWriter` calls `write` for each queued entry and `flush` to make entries durable. Persistent state is owned by concrete writer backends. Dependencies are generated journal protobufs and `JournalClosedException`. Risks include callers assuming `write` is durable without `flush`, close/flush races, and backend-specific error mapping. Tests should target concrete writers for sequence numbering, durability after flush, closed behavior, partial write recovery, and idempotent close.
