<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h -->
# sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h

## Purpose
This internal header implements `local_lock.h` for both normal and PREEMPT_RT kernels. It is deliberately not included directly and carries the low-level preemption, migration, IRQ, lockdep, and trylock behavior.

## Important APIs, Types, and Functions
On non-RT kernels it defines `local_lock_t` and `local_trylock_t` context lock structures with optional `lockdep_map`, owner, and acquired state. Internal macros include `INIT_LOCAL_LOCK`, `__local_lock_init`, `__local_lock`, IRQ variants, trylock variants, release variants, nested-BH helpers, and `__local_lock_is_locked`. On PREEMPT_RT, both lock types map to `spinlock_t`, using `migrate_disable()` plus spin locking.

## Control Flow
Non-RT acquisition disables preemption or IRQs and records lockdep ownership; trylock checks an acquired byte and may fail without blocking. Release clears owner/acquired state then reenables preemption or IRQs. RT acquisition disables migration and takes a per-CPU spinlock, leaving the section preemptible.

## State and Persistence Behavior
Runtime state is per-CPU lock contents, owner tracking, lockdep maps, and trylock acquired bytes or RT spinlock state. No persistence exists.

## Dependencies and Integration Points
It depends on per-CPU definitions, irqflags, lockdep, debug locks, current task, scheduler state, and spinlocks under RT. `local_lock.h` is the public integration point.

## Risks and Test Signals
Risks include direct inclusion, incorrect assumptions about preemption/IRQ state across RT and non-RT, trylock use from NMI/hardirq on RT, and misuse of `local_lock_is_locked` without disabled migration/preemption. Test signals are lockdep owner warnings, PREEMPT_RT test boots, context tracking assertions, and trylock failure-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h -->
