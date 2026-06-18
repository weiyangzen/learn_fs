# sources/distributed-fs/ceph-client/include/linux/mutex.h

Purpose: declares the main kernel mutex API, initializers, lockdep/debug integration, PREEMPT_RT variants, device-managed initialization, lock operations, and cleanup-based guard helpers.

Important APIs and types: `mutex_init()`, `mutex_init_with_key()`, `__MUTEX_INITIALIZER()`, and `DEFINE_MUTEX()` initialize mutexes with debug and lockdep metadata. Non-RT builds initialize `owner`, `wait_lock`, `first_waiter`, and optional debug fields; PREEMPT_RT builds wrap `rt_mutex_base`. Locking APIs include `mutex_lock()`, `mutex_lock_interruptible()`, `mutex_lock_killable()`, `mutex_lock_io()`, nested/nest-lock variants under lockdep, `mutex_trylock()`, `mutex_unlock()`, `mutex_is_locked()`, `mutex_get_owner()`, and `atomic_dec_and_mutex_lock()`. `devm_mutex_init()` registers debug teardown when `CONFIG_DEBUG_MUTEXES` needs it. `DEFINE_LOCK_GUARD_1*` and class constructor macros provide scoped cleanup lock guards for mutex, try, interruptible, killable, and init use.

Control flow: static locks are created with `DEFINE_MUTEX`, dynamic locks call `mutex_init()`, and callers acquire/release through blocking, interruptible, killable, trylock, or I/O-accounted paths. With `CONFIG_DEBUG_LOCK_ALLOC`, public APIs route through nested forms so lockdep receives subclass or nesting relationships. With PREEMPT_RT, the same API maps to rtmutex internals to provide priority inheritance semantics.

State and persistence: mutex state is in-memory synchronization state: owner, waiters, lockdep map, optional magic/debug fields, or rtmutex state. It is not persistent and must not be copied, memset-reinitialized while held, freed while held, or used from interrupt context.

Dependencies and integration points: depends on current task, atomic operations, spinlock and osq types, lockdep, debug locks, cleanup guard macros, RT mutexes when enabled, and device-managed resource cleanup. It is a core synchronization contract used across the kernel.

Risks and test signals: risks include recursive locking, non-owner unlock, reinitializing or freeing held locks, ignoring return values from interruptible/killable APIs, lockdep subclass mistakes, PREEMPT_RT semantic drift, and misuse of scoped guards that changes unlock timing. Test signals include `CONFIG_DEBUG_MUTEXES`, `CONFIG_DEBUG_LOCK_ALLOC`, lockdep cycle detection, PREEMPT_RT builds, interruptible signal handling, trylock contention, devm teardown, and cleanup guard scope-exit paths.
