# sources/distributed-fs/ceph-client/kernel/locking/spinlock_rt.c

## Purpose
Provides PREEMPT_RT substitutions for regular spinlocks and rwlocks. Instead of raw busy-waiting, these locks are backed by rtmutexes, preserve task state while blocking, disable migration, and hold RCU read-side state to approximate non-RT spinlock semantics.

## Important APIs, Types, and Functions
- Spinlock exports: `rt_spin_lock()`, `rt_spin_lock_nested()`, `rt_spin_lock_nest_lock()`, `rt_spin_unlock()`, `rt_spin_lock_unlock()`, `rt_spin_trylock()`, `rt_spin_trylock_bh()`, and `__rt_spin_lock_init()`.
- Rwlock exports: `rt_read_lock()`, `rt_read_trylock()`, `rt_read_unlock()`, `rt_write_lock()`, `rt_write_lock_nested()`, `rt_write_trylock()`, `rt_write_unlock()`, and `__rt_rwlock_init()`.
- Internal helpers include `rtlock_lock()`, `__rt_spin_lock()`, `__rt_spin_trylock()`, and macro adapters for `rwbase_rt.c`.

## Control Flow
Spin lock acquisition checks reschedule rules, acquires lockdep, tries rtmutex owner cmpxchg, and falls back to `rtlock_slowlock()`. On success it enters RCU read-side and disables migration. Unlock releases lockdep, enables migration, exits RCU, and release-cmpxchg's the rtmutex or slow-unlocks. Rwlocks use `rwbase_rt.c`: reads and writes acquire through the rwbase reader/writer protocol, then enter RCU and disable migration; unlock reverses those state changes and releases the rwbase lock.

## State and Persistence
State is in the lock's embedded `rt_mutex_base` or `rwbase_rt`, lockdep map, task saved wait state, migration disable count, and RCU nesting. No persistent storage.

## Dependencies and Integration Points
Depends on `rtmutex.c` with `RT_MUTEX_BUILD_SPINLOCKS`, `rwbase_rt.c`, lockdep, RCU preempt depth, migration control, softirq controls for `_bh`, and PREEMPT_RT scheduler helpers such as `schedule_rtlock()`.

## Risks
These locks may sleep, so code assuming non-RT spinlocks are always atomic must use raw spinlocks where required. Correct preservation/restoration of task state prevents missed wakeups while blocked on rtlocks. RCU and migration ordering differs subtly between read and write unlock paths and must preserve non-RT semantics.

## Test Signals
PREEMPT_RT lock torture, sleep-in-spinlock audits, lockdep nesting tests, `rt_spin_trylock_bh()` softirq state tests, migration/RCU nesting assertions, rtlock contention traces, and rwlock reader/writer starvation stress.
