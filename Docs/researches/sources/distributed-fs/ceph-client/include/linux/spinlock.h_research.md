<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock.h

Purpose: Defines the generic Linux spinlock interface used by the Ceph client source snapshot. It is the umbrella header that selects SMP, UP, debug, and PREEMPT_RT behavior and exposes the public `raw_spin_*()`, `spin_*()`, `rwlock_*()` integration, atomic decrement-and-lock helpers, bucket lock allocation, and cleanup-based lock guards.

Important APIs/types/functions: `raw_spin_lock_init()`, `raw_spin_is_locked()`, `raw_spin_lock_irqsave()`, `raw_spin_unlock_irqrestore()`, `spinlock_check()`, `spin_lock_init()`, `spin_lock*()`, `spin_unlock*()`, `spin_trylock*()`, `spin_is_locked()`, `spin_is_contended()`, `assert_spin_locked()`, `spin_needbreak()`, `rwlock_needbreak()`, `atomic_dec_and_lock()`, `atomic_dec_and_raw_lock()`, `alloc_bucket_spinlocks()`, and many `DEFINE_LOCK_GUARD_1*()` guard classes.

Control flow: The header first pulls generic type declarations, then chooses architecture spin primitives from `<asm/spinlock.h>` on SMP or `spinlock_up.h` on UP. It wraps low-level `arch_spin_*()` operations in `do_raw_spin_*()` unless debug spinlocks provide out-of-line checking. It includes either `spinlock_api_smp.h` or `spinlock_api_up.h` for `_raw_*()` operations, then maps ordinary `spinlock_t` to raw spinlocks when `CONFIG_PREEMPT_RT` is disabled or includes `spinlock_rt.h` for sleeping RT locks.

State and persistence behavior: No persistent storage is managed here, but lock state is stored in `raw_spinlock_t`/`spinlock_t`, lockdep maps, debug ownership fields, IRQ flags, preemption counters, and memory-ordering barriers. `smp_mb__after_spinlock()` documents RCsc ordering expectations and defaults to `kcsan_mb()` if the architecture does not override it.

Dependencies: Depends on preemption, IRQ flags, bottom halves, lockdep, cleanup guards, architecture barriers, MMI/O write barriers, `spinlock_types.h`, `spinlock_api_{smp,up}.h`, and optionally `rwlock.h`/`spinlock_rt.h`. Kernel C annotations such as `__acquires`, `__releases`, and `typecheck()` are part of the contract.

Integration points: Used by most in-kernel synchronization users, including SSB headers in this subset. PREEMPT_RT integration is a major compatibility point: non-RT callers get raw spinning semantics while RT callers get rtmutex-backed `spinlock_t` semantics. Cleanup guard macros allow lexical lock management via compiler cleanup infrastructure.

Risks: Misusing IRQ-save flags, mixing raw and regular locks, relying on `spin_is_locked()` for synchronization, or assuming `spinlock_t` always spins can break across UP/debug/RT configurations. Architecture implementations must satisfy the documented memory ordering after lock acquisition.

Test signals: Build coverage across `CONFIG_SMP`, UP, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_DEBUG_LOCK_ALLOC`, and `CONFIG_PREEMPT_RT`; lockdep tests for nested and nest-lock paths; KCSAN/RCU scheduler tests for `smp_mb__after_spinlock()` ordering; runtime stress using `atomic_dec_and_lock*()` and guard-class lock/unlock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock.h -->
