# sources/distributed-fs/ceph-client/kernel/locking/spinlock.c

## Purpose
Provides out-of-line raw spinlock and raw rwlock API functions for SMP/debug builds, plus generic lock-break spinning variants when configured. These wrappers connect architecture raw lock primitives with preemption/interrupt state, lockdep annotations, exports, and profiling boundaries.

## Important APIs, Types, and Functions
- Exports raw spin APIs such as `_raw_spin_trylock()`, `_raw_spin_lock()`, `_raw_spin_lock_irqsave()`, `_raw_spin_unlock_irqrestore()`, and `_raw_spin_lock_nested()`.
- Non-RT exports raw rwlock APIs such as `_raw_read_lock()`, `_raw_write_lock()`, `_raw_write_lock_nested()`, and their irq/bh/unlock variants.
- `BUILD_LOCK_OPS()` generates preemption-friendly lock-break loops when generic lockbreak is enabled without debug lock allocation.
- `in_lock_functions()` reports whether an address lies in lock text.
- `lockdep_assert_in_softirq_func()` is exported for PREEMPT_RT prove-locking builds.

## Control Flow
Most functions are thin noinline wrappers around inline `__raw_*` operations unless the config inlines them elsewhere. Under generic lockbreak, generated loops disable preemption, try the raw lock, re-enable preemption on failure, and relax toward the owner before retrying. IRQ and BH variants preserve interrupt/softirq state around those lock attempts. Debug lock allocation variants perform explicit lockdep acquire before contended raw spin acquisition.

## State and Persistence
No lock state is owned here except optional per-CPU `__mmiowb_state`. The functions mutate caller-supplied raw spin/rwlocks and CPU interrupt/preemption state.

## Dependencies and Integration Points
Depends on architecture raw lock operations, preemption, interrupt APIs, lockdep, debug locks, MMIO write barriers, and exported kernel symbol users. Raw rwlock wrappers are omitted under PREEMPT_RT because RT rwlocks are implemented elsewhere.

## Risks
Changing stack frames can affect architecture profiling. IRQ/BH/preemption ordering must remain exact or lockdep and interrupt masking semantics break. Generic lockbreak trades fairness and preemptibility against raw spin behavior and must not be used where lockdep assumes interrupts remain disabled through acquire.

## Test Signals
Build matrix for inline/non-inline, generic lockbreak, debug lock allocation, PREEMPT_RT, and MMIOWB. Runtime signals include lockdep reports, interrupt state assertions, profiling `in_lock_functions()`, and raw spin/rwlock torture.
