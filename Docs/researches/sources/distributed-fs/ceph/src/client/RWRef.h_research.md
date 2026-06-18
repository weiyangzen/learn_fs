# sources/distributed-fs/ceph/src/client/RWRef.h

## Purpose
`RWRef.h` defines a lightweight state-gated reader/writer reference mechanism used by the client lifecycle. Readers increment a refcount only when a required state predicate is satisfied; writers transition state and can wait for active readers to drain.

## Important APIs, Types, and Functions
`RWRefState<T>` stores current state, lock, condition variable, reader count, and virtual predicates `check_reader_state()`, `check_writer_state()`, and `is_valid_state()`. `RWRef<T>` is an RAII object with `is_state_satisfied()`, `update_state()`, `is_first_writer()`, and `wait_readers_done()`.

## Control Flow
Reader operations construct `RWRef(state, required, true)`. If allowed, `reader_cnt` increments and destructor decrements/notifies. Writer operations construct `RWRef(state, next_state, false)`, transition state if permitted, then call `wait_readers_done()` before completing lifecycle-sensitive work. Client mount/init state structs specialize the predicates in `Client.h`.

## State and Persistence Behavior
All state is in-memory synchronization state. It avoids holding a reader lock during IO while still blocking lifecycle writers until in-flight readers leave.

## Dependencies and Integration Points
It depends on Ceph mutex/condition variable wrappers and assertions. `Client` uses it for initialize and mount state transitions.

## Risks and Edge Cases
Writer construction sets `satisfied=true` even if it is not the first writer; callers must inspect `is_first_writer()` when that distinction matters. There is no reader wait path; failed readers must return or retry at a higher layer. Predicate correctness is entirely delegated to subclasses. Destructors lock state, so misuse during object teardown can deadlock if state outlives assumptions fail.

## Test Signals
Concurrent readers during unmount, failed readers in wrong state, first-writer versus subsequent-writer behavior, writer wait for reader drain, state update validity assertions, and no deadlock with unrelated locks.
