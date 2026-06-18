<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h

Purpose: Declares and optionally inlines raw spinlock operations for SMP or debug builds. It is internal to `spinlock.h` and guarded against direct inclusion.

Important APIs/types/functions: `_raw_spin_lock()`, `_raw_spin_lock_nested()`, `_raw_spin_lock_nest_lock()`, `_raw_spin_lock_bh()`, `_raw_spin_lock_irq()`, `_raw_spin_lock_irqsave()`, `_raw_spin_trylock()`, `_raw_spin_trylock_irq()`, `_raw_spin_trylock_irqsave()`, `_raw_spin_unlock*()`, `_raw_spin_trylock_bh()`, and `in_lock_functions()`.

Control flow: Function prototypes are provided for out-of-line implementations in `kernel/spinlock.c`. Configuration macros such as `CONFIG_INLINE_SPIN_LOCK` redirect public `_raw_*()` names to inline `__raw_*()` functions. Inline lock acquisition disables preemption or interrupts/bottom halves, records lockdep acquisition, then calls `LOCK_CONTENDED()` with `do_raw_spin_trylock()`/`do_raw_spin_lock()`. Unlock releases lockdep state, performs raw unlock, then restores preemption/IRQ/BH state.

State and persistence behavior: Updates preemption counters, local IRQ/BH disable state, lockdep maps, and architecture lock words. Trylock paths restore state on failure.

Dependencies: Requires `spinlock.h` to provide `raw_spinlock_t`, `do_raw_spin_*()`, lockdep helpers, local IRQ/BH helpers, and architecture implementations.

Integration points: Included by `spinlock.h` for SMP and debug spinlock builds. Pulls in `rwlock_api_smp.h` when PREEMPT_RT is not active.

Risks: Ordering and state restoration bugs can leave preemption/IRQs disabled or lockdep inconsistent. Lockdep intentionally avoids lockbreak preempt-spin ops in some configurations, so timing differs by config.

Test signals: Lockdep acquisition/release tests, trylock failure tests verifying IRQ/BH/preempt restoration, SMP contention stress, and builds for all inline/uninline configuration combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h -->
