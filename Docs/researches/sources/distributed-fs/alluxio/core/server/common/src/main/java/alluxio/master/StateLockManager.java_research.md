# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockManager.java

## Purpose
`StateLockManager` coordinates shared state-changing RPCs with exclusive operations such as metadata backups.

## Important APIs, Types, And Functions
`lockShared` acquires an interruptible read lock and tracks waiters/holders by thread. `lockExclusive` performs a configurable grace cycle, optionally activates an interrupt cycle, then acquires the write lock or times out. `mastersStartedCallback` opens an exclusive-only maintenance window after state load. Accessors expose shared holders and interrupt-cycle state.

## Control Flow, State, Dependencies, Risks, And Tests
Shared callers are blocked during exclusive-only startup and can be interrupted while backup forces the write lock. Exclusive callers use `StateLockOptions`, optional `beforeAttempt`, configured forced duration, and a scheduler that interrupts registered shared threads. State is in-memory synchronization state; persistence is protected by ensuring journals and checkpoints see quiescent master state. Dependencies include `ReentrantReadWriteLock`, config keys, `ConcurrentHashSet`, `RetryUtils`, and `LockResource`. Risks include holder tracking cleanup bugs, interrupting active shared state operations, scheduler lifetime leaks, recursion warning noise, and fair-lock contention. Tests should cover grace timeout/forced modes, interrupt cycle ref-counting, exclusive-only window, shared lock cleanup, before-attempt failures, and high recursion logging.
