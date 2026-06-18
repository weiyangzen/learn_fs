# sources/distributed-fs/ceph-client/kernel/locking/rwbase_rt.c

## Purpose
Common PREEMPT_RT base implementation for rw semaphores and rwlocks backed by an rt_mutex plus an atomic reader count. It gives writers priority inheritance through rt_mutex while allowing fast reader increments when no writer has removed the reader bias.

## Important APIs, Types, and Functions
- Reader helpers: `rwbase_read_trylock()`, `__rwbase_read_lock()`, `rwbase_read_lock()`, `__rwbase_read_unlock()`, and `rwbase_read_unlock()`.
- Writer helpers: `rwbase_write_lock()`, `rwbase_write_trylock()`, `rwbase_write_unlock()`, `rwbase_write_downgrade()`, `__rwbase_write_unlock()`, and `__rwbase_write_trylock()`.
- Behavior is parameterized by macros supplied by `rwsem.c` or `spinlock_rt.c` for scheduling, signal handling, and rtmutex operations.

## Control Flow
Readers first try to increment `readers` while it is negative, meaning `READER_BIAS` is present. If fast path fails, a reader takes the underlying rtmutex slow path under `wait_lock`, increments readers once no writer is active, drops `wait_lock`, and unlocks the rtmutex. Writers first lock the rtmutex, subtract `READER_BIAS` to force new readers slow, then wait under `wait_lock` until active readers drain and set `WRITER_BIAS`. Unlock restores reader bias with release ordering and unlocks the rtmutex; downgrade restores bias while accounting the writer as one reader.

## State and Persistence
State is in `struct rwbase_rt`: an `rt_mutex_base` plus atomic `readers` counter carrying reader bias and writer bias. No persistence.

## Dependencies and Integration Points
Included by both `rwsem.c` and `spinlock_rt.c` after defining macro adapters. Integrates with rtmutex PI, wake queues, scheduler/task state preservation, lock trace events, and lockdep in wrappers.

## Risks
The implementation is intentionally not writer-fair for readers on RT; writer starvation is documented as possible. Fast-path acquire/release ordering must pair with writer bias changes. Macro adapter mistakes can break signal behavior for semaphores versus non-signalable RT rwlocks.

## Test Signals
PREEMPT_RT rwsem and rwlock tests with mixed readers/writers, writer starvation stress, signalable `down_write_killable()` paths, lockdep for rtmutex nesting, and trace contention for RT read/write waits.
