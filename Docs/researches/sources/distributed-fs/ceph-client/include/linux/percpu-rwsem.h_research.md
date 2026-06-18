<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h

## Purpose
Defines a reader-optimized read/write semaphore where readers normally update per-CPU counters and writers use `rcu_sync` plus wait queues to block new readers and wait for existing readers to drain.

## Important APIs, Types, And Functions
- `struct percpu_rw_semaphore` contains `struct rcu_sync rss`, per-CPU `read_count`, writer `rcuwait`, waiter queue, atomic `block`, and optional lockdep map.
- Static initializers: `DEFINE_PERCPU_RWSEM()` and `DEFINE_STATIC_PERCPU_RWSEM()`.
- Reader APIs: `percpu_down_read()`, `percpu_down_read_freezable()`, `percpu_down_read_trylock()`, `percpu_up_read()`, and internal `__percpu_down_read()`.
- Writer APIs: `percpu_down_write()` and `percpu_up_write()`.
- State/lockdep helpers: `percpu_is_read_locked()`, `percpu_is_write_locked()`, `percpu_init_rwsem()`, `percpu_free_rwsem()`, `percpu_rwsem_is_write_held()`, `percpu_rwsem_is_held()`, `percpu_rwsem_assert_held()`, `percpu_rwsem_release()`, and `percpu_rwsem_acquire()`.
- Guard macros define cleanup-style read/write guards.

## Control Flow
Fast-path readers sleep-check, acquire lockdep read state, disable preemption, and increment the current CPU counter if `rcu_sync_is_idle()`. If a writer is active or pending, they enter `__percpu_down_read()`. Unlock decrements the per-CPU count and, on slow path, uses a memory barrier and wakes the blocked writer. Writers use external functions to block new readers, synchronize through `rcu_sync`, wait for per-CPU counts to drain, and release afterward.

## State And Persistence
Persistent synchronization state is the per-CPU `read_count`, `rcu_sync` state, writer wait object, wait queue, and `block` atomic. Static definitions allocate a named per-CPU counter and initialized semaphore object.

## Dependencies And Integration Points
Depends on percpu variables, RCU sync, rcuwait, wait queues, atomics, lockdep, preemption control, and cleanup guards. It is used where read-side sections are frequent and writers are rare but need global exclusion.

## Risks And Edge Cases
Risks include missing `percpu_up_read()`, sleeping in contexts where `might_sleep()` is invalid, writer starvation or missed wakeups if barriers are broken, using read locks while CPU hotplug or RCU synchronization assumptions change, and lockdep false negatives if manual acquire/release helpers are misused.

## Test Signals
Stress many readers with rare writers, trylock failure under writer pressure, freezable readers, lockdep assertions, CPU hotplug during read-heavy workloads, writer wait/wakeup correctness, and KCSAN/lockdep runs for barrier and lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h -->
