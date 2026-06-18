<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/local_lock.h

## Purpose
This header exposes per-CPU local lock APIs. It gives callers a uniform way to protect CPU-local data across non-RT and PREEMPT_RT kernels while preserving lockdep annotations.

## Important APIs, Types, and Functions
Macros include `local_lock_init`, `local_lock`, `local_lock_irq`, `local_lock_irqsave`, `local_unlock`, `local_unlock_irq`, `local_unlock_irqrestore`, `local_trylock_init`, `local_trylock`, `local_trylock_irqsave`, `local_lock_is_locked`, `local_lock_nested_bh`, and `local_unlock_nested_bh`. It also declares lock-guard helper classes for scoped cleanup.

## Control Flow
Public macros map a per-CPU base lock to the current CPU instance with `__this_cpu_local_lock()`, then call implementation macros from `local_lock_internal.h`. IRQ variants save or modify interrupt state as appropriate.

## State and Persistence Behavior
State is per-CPU lock instances supplied by callers. No state persists beyond runtime; ownership and acquired state are implementation-dependent.

## Dependencies and Integration Points
It depends on `local_lock_internal.h`, lock guard infrastructure, per-CPU variables, IRQ state handling, and lockdep. It integrates with code that must remain correct under PREEMPT_RT semantics.

## Risks and Test Signals
Risks include using a local lock for cross-CPU protection, passing non-per-CPU storage to per-CPU macros, and assuming IRQ disabling on RT where semantics differ. Test signals are PREEMPT_RT builds, lockdep assertions, IRQ/preemption context tests, and scoped guard compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock.h -->
