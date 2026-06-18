# sources/distributed-fs/ceph-client/kernel/locking/percpu-rwsem.c

## Purpose
Implements per-CPU read/write semaphores optimized for frequent readers. Readers usually increment a per-CPU counter without taking a global lock; writers block new readers, wait for active per-CPU counters to drain, and then hold exclusive access.

## Important APIs, Types, and Functions
- Exports `__percpu_init_rwsem()`, `percpu_free_rwsem()`, `__percpu_down_read()`, `percpu_is_read_locked()`, `percpu_down_write()`, and `percpu_up_write()`.
- Fast reader path is `__percpu_down_read_trylock()`.
- Writer exclusion is `__percpu_down_write_trylock()`.
- Slow waiter handling uses `percpu_rwsem_wait()` and `percpu_rwsem_wake_function()`.
- Reader drain test is `readers_active_check()`.

## Control Flow
Initialization allocates `read_count` per CPU, initializes `rcu_sync`, `rcuwait`, wait queue, and `block`. A reader disables preemption in the caller path, increments its CPU counter, issues a memory barrier, and succeeds if `block` is not set; otherwise it decrements and wakes the writer. A writer enters `rcu_sync`, atomically sets `block`, optionally sleeps in FIFO wait queue order, then uses `rcuwait_wait_event()` until all per-CPU counts sum to zero. Unlock clears `block` with release ordering, wakes one queued operation through the custom wait function, and exits `rcu_sync` so readers can regain the fast path after a grace period.

## State and Persistence
State is in `struct percpu_rw_semaphore`: per-CPU `read_count`, `rcu_sync rss`, `rcuwait writer`, FIFO `waiters`, and atomic `block`. No persistence beyond in-memory synchronization.

## Dependencies and Integration Points
Depends on per-CPU allocation, RCU sync, rcuwait, wait queues, scheduler state, lockdep, trace events, and atomic ordering. It is used by subsystems needing extremely cheap read-side critical sections with occasional global write exclusion.

## Risks
The memory-barrier pairs around reader count and writer block are critical. Missing `percpu_free_rwsem()` after successful init leaks per-CPU storage. Writer latency can be high with long read-side sections. The wake function intentionally wakes readers until a writer is acquired, so its return protocol must match wait queue expectations.

## Test Signals
Test with lockdep, RCU stall detection, writer starvation tests, freezer paths through the `freeze` argument, and fault injection for `alloc_percpu()` failure. Runtime tracepoints for percpu read/write contention indicate slow-path behavior.
