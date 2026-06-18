# sources/distributed-fs/ceph-client/include/linux/rwsem.h

## Purpose
`rwsem.h` declares sleeping reader/writer semaphores. It provides initialization, lock state queries, lockdep assertions, acquire/release APIs, guard constructors, downgrade support, and non-owner read variants.

## Important APIs, types, and functions
Important macros and APIs include `RWSEM_UNLOCKED_VALUE`, `RWSEM_WRITER_LOCKED`, `__RWSEM_INITIALIZER`, `DECLARE_RWSEM()`, `init_rwsem()`, `rwsem_is_locked()`, `rwsem_assert_held()`, `rwsem_assert_held_write()`, `rwsem_is_contended()`, `rwsem_owner()`, `is_rwsem_reader_owned()`, `down_read()`, `down_read_interruptible()`, `down_read_killable()`, `down_read_trylock()`, `down_write()`, `down_write_killable()`, `down_write_trylock()`, `up_read()`, `up_write()`, `downgrade_write()`, nested lock variants, lock-guard class constructors, `down_read_non_owner()`, and `up_read_non_owner()`.

## Control flow, state, and persistence
Readers and writers sleep when they cannot acquire the semaphore. Non-RT builds use an atomic count, waiter list, owner tracking, optional optimistic spinning queue, and lockdep map; RT builds use RT-specific rwsem types and operations. Guard constructors create scoped acquire/release wrappers for cleanup-style locking. State persists in `struct rw_semaphore` for the protected object.

## Dependencies and integration points
It depends on atomic longs, wait queues, optimistic spin queues, lockdep, mutex/RT internals, cleanup guards, scheduler/task ownership, and PREEMPT_RT configuration. It is used by MM (`mmap_lock`), filesystems, module/sysfs paths, and many sleeping read-mostly kernel subsystems.

## Risks and test signals
Risks include calling rwsems from atomic context, read/write lock ordering deadlocks, missed unlocks on error paths, ownership assertion false positives for non-owner read APIs, starvation/optimistic spinning issues, and RT semantic differences. Test signals include lockdep assertions, rwsem locktorture, interruptible/killable return-path tests, downgrade tests, mmap-lock stress, scoped-guard cleanup checks, and RT/non-RT build coverage.
