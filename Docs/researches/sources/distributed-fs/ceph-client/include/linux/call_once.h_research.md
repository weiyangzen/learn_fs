## sources/distributed-fs/ceph-client/include/linux/call_once.h

**Purpose:** This header provides a small synchronization primitive to run an initialization callback exactly once after it succeeds.

**Important APIs/types/functions:** State constants are `ONCE_NOT_STARTED`, `ONCE_RUNNING`, and `ONCE_COMPLETED`. `struct once` stores an atomic state and mutex. `once_init()` initializes the object with a lock class key. `call_once(struct once *once, int (*cb)(struct once *))` runs the callback if not completed.

**Control flow, state, persistence:** Fast path uses `atomic_read_acquire()` to skip locking once completed. Slow path takes the mutex, rejects unexpected state, marks running, invokes `cb`, resets to not-started on negative return, or stores completed with release ordering on success. State persists in the `struct once` object for the lifetime of the owning subsystem.

**Dependencies/integration:** Depends on atomics, mutexes, lockdep lock classes, and guard-based mutex cleanup.

**Risks and test signals:** Risks include failing to call `once_init()`, callback recursion on the same object, callbacks that return success before publishing all state, and unexpected `ONCE_RUNNING` states causing `-EINVAL`. Test signals include concurrent caller stress tests, failure-then-retry behavior, lockdep checks, and memory-order tests for initialized data visibility.
