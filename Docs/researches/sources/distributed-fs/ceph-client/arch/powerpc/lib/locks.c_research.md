# sources/distributed-fs/ceph-client/arch/powerpc/lib/locks.c

This file implements SPLPAR-aware yielding helpers for classic PowerPC spinlocks and rwlocks when queued spinlocks are not selected. Under `CONFIG_PPC_SPLPAR`, it exports `splpar_spin_yield(arch_spinlock_t *lock)` and defines `splpar_rw_yield(arch_rwlock_t *rw)`.

The spinlock path reads `lock->slock`, returns if unlocked, extracts the holder CPU from low bits, validates it, samples the holder's hypervisor yield count, and returns if the vCPU is currently running. After a read memory barrier, it verifies the lock word is unchanged and calls `yield_to_preempted(holder_cpu, yield_count)`. The rwlock path is similar but only yields when the rwlock value is negative, indicating a writer is present and the holder CPU can be decoded.

State is read-only lock state plus hypervisor dispatch/yield counters; no persistent kernel state is updated here. Dependencies include SPLPAR hypervisor calls, `yield_count_of`, `yield_to_preempted`, CPU numbering, and lock word encoding. Integration is the lock slow path on shared-processor PowerPC systems without `CONFIG_PPC_QUEUED_SPINLOCKS`. Risks include stale holder CPU fields, yielding when the lock changed, and lock encoding changes. Test signals are shared-LPAR contention benchmarks, lockdep/smp stress, and builds with SPLPAR enabled and queued spinlocks disabled.
