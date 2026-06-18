<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_up.h

Purpose: Provides UP implementations of `arch_spin_*()` and `arch_rwlock_*()` primitives used by generic spinlock wrappers.

Important APIs/types/functions: `arch_spin_is_locked()`, `arch_spin_lock()`, `arch_spin_trylock()`, `arch_spin_unlock()`, `arch_spin_is_contended()`, and read/write lock macros.

Control flow: Debug UP spinlocks mutate the `slock` field and use compiler barriers to constrain instruction movement. Non-debug UP primitives are barrier-only no-ops, with trylocks always returning success. RW lock primitives are always barrier-only.

State and persistence behavior: Debug UP spinlocks store a simple locked/unlocked state; non-debug locks store none. Compiler barriers remain important for faulting memory accesses and code motion.

Dependencies: Requires inclusion from `spinlock.h` and uses `asm/processor.h`/`asm/barrier.h`.

Integration points: Selected by `spinlock.h` on non-SMP builds before the generic API layer wraps preemption and IRQ semantics.

Risks: The absence of atomic operations is correct only for UP. Bugs hidden by always-success trylocks can appear on SMP.

Test signals: UP debug lock misuse tests, compiler build coverage, and sparse lock annotation behavior through the upper API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_up.h -->
