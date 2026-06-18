<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h

Purpose: Provides PREEMPT_RT semantics for `spinlock_t` by mapping regular spinlocks to rtmutex-backed sleeping locks while preserving the source-level spinlock API.

Important APIs/types/functions: `__spin_lock_init()`, `spin_lock_init()`, `local_spin_lock_init()`, `rt_spin_lock()`, `rt_spin_lock_nested()`, `rt_spin_lock_nest_lock()`, `rt_spin_unlock()`, `rt_spin_trylock()`, `rt_spin_trylock_bh()`, `spin_lock*()`, `spin_unlock*()`, `spin_trylock*()`, `spin_is_locked()`, and `assert_spin_locked()`.

Control flow: Initialization sets up the embedded `rt_mutex_base` and optional lockdep metadata. Normal lock operations call `rt_spin_lock()`; BH variants disable/enable bottom halves around the rt lock; IRQ and irqsave variants do not actually disable interrupts and set saved flags to zero because RT spinlocks may sleep.

State and persistence behavior: Lock state lives in the embedded rtmutex base and lockdep map. IRQ-save flags are intentionally synthetic. Contention is not reported through `spin_is_contended()`.

Dependencies: Requires `spinlock.h` inclusion context, `rtmutex.h` through `spinlock_types.h`, lockdep type checking, local BH helpers, and `rwlock_rt.h`.

Integration points: Included by `spinlock.h` when `CONFIG_PREEMPT_RT` is enabled. Callers that need true non-sleeping exclusion must use raw spinlocks, not regular `spinlock_t`.

Risks: Code assuming interrupts are disabled inside `spin_lock_irqsave()` or assuming locks cannot sleep is wrong on RT. Such code may deadlock or violate atomic context constraints.

Test signals: PREEMPT_RT build and runtime tests, lockdep nesting tests, atomic-context misuse detection, and tests that verify flags are handled safely by irqsave/restore call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h -->
