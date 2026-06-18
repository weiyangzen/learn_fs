# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/StateChangeJournalContext.java

## Purpose
`StateChangeJournalContext` ties a journal context lifetime to a held shared state lock.

## Important APIs, Types, And Functions
It wraps `JournalContext` and `LockResource`. `append` and `flush` delegate. `close` closes the journal context, then releases the state lock in a finally block.

## Control Flow, State, Dependencies, Risks, And Tests
The wrapper ensures state-changing RPCs keep the shared lock until their journal context has closed and flushed. It has no persistence beyond delegated journal behavior. Dependencies are `LockResource`, `JournalContext`, and `Preconditions`. Risks include non-thread-safe use, caller failing to close, and underlying close hanging while holding shared lock. Tests should cover close ordering, lock release on close exception, delegate append/flush, and interaction with `AbstractMaster.createJournalContext`.
