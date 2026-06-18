<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h

Purpose: selects generic queued spinlock and queued rwlock implementations for Xtensa and defines `smp_mb__after_spinlock()` as a full SMP memory barrier.

Control flow is in included qspinlock/qrwlock code; this header supplies the arch barrier hook. State is lock word state managed by generic locking primitives. Dependencies include `asm/barrier.h`, `asm/qspinlock.h`, and `asm/qrwlock.h`. Integration points are all kernel spinlock/rwlock users, scheduler and interrupt synchronization, and SMP memory ordering. Risks center on insufficient barrier semantics after lock acquisition or mismatched atomic implementation support. Test signals include locktorture, SMP stress, lockdep, atomic/queued lock build coverage, and memory-order litmus-style failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h -->
