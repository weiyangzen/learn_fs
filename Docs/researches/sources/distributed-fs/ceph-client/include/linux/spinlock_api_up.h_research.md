<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h

Purpose: Implements raw spinlock and rwlock APIs for UP non-debug builds, where no real inter-CPU exclusion is required but compiler annotations, IRQ state, bottom-half state, and preemption accounting still matter.

Important APIs/types/functions: Macro implementations for `_raw_spin_lock*()`, `_raw_read_lock*()`, `_raw_write_lock*()`, `_raw_spin_unlock*()`, read/write unlocks, trylock variants, `in_lock_functions()`, and `assert_raw_spin_locked()`.

Control flow: Lock macros disable preemption, IRQs, or bottom halves as requested, then issue sparse/lock annotations. Trylock variants always succeed after applying the corresponding state changes. Unlock macros reverse the state changes and release annotations.

State and persistence behavior: No hardware lock word is used in non-debug UP mode. Runtime state is limited to preempt count and local IRQ/BH state.

Dependencies: Must only be included from `spinlock.h`, and relies on preemption, IRQ, softirq, and sparse annotation helpers.

Integration points: Selected by `spinlock.h` when neither SMP nor debug spinlock support requires the SMP API path.

Risks: Since trylocks always succeed and lock state is not represented, code that incorrectly relies on lock contention behavior may pass on UP and fail on SMP. Incorrect flag variable types are caught by outer macros in `spinlock.h`.

Test signals: UP build tests, sparse lock annotation checks, and unit-like compile tests for all IRQ/BH/irqsave variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h -->
