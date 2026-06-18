# sources/distributed-fs/eos/mgm/tgc/BlockingFlag.hh

## Purpose
`BlockingFlag.hh` defines a simple condition-variable backed boolean flag. It starts false, can be waited on with a timeout, and can be set true to wake all waiters.

## Important APIs, Types, And Functions
`BlockingFlag` provides a constructor, `operator bool() const`, templated `waitForTrue(Duration) noexcept`, and `setToTrue()`. State is protected by `m_mutex` and waiters use `m_cond`.

## Control Flow
Readers lock the mutex and return the current flag. `waitForTrue()` waits for the predicate `m_flag` for the specified duration and catches/logs any exception before returning false. `setToTrue()` locks, sets the flag, and notifies all waiting threads.

## State And Persistence
State is one in-memory boolean. There is no reset API, so the object is a one-way latch from false to true.

## Dependencies And Integration Points
The file uses standard mutex and condition-variable primitives and EOS logging via `eos_static_err`. It is suitable for worker stop signals or test synchronization in the tape-GC subsystem.

## Risks And Edge Cases
`notify_all()` is called while holding the mutex; this is correct but may wake waiters that immediately contend for the lock. Because there is no reset, reusing the same object across lifecycle phases would leave it permanently true. The header relies on logging declarations being available through included namespace context or transitive includes.

## Test Signals
Tests should cover initial false state, timeout returning false, wakeup returning true, bool conversion after setting, multiple waiters, and repeated waits after the flag is already true.
