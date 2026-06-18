<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h

Purpose: adapts queued spinlocks for real-time or raw queued spinlock configurations on x86. Important APIs are the architecture include glue and paravirt lock initialization/unlock hooks selected by config.

Control flow: compilation routes lock users to either generic queued spinlock behavior or architecture/paravirt variants. State is the underlying qspinlock word. Dependencies include qspinlock, paravirt spinlocks, and real-time locking configuration. Risks are configuration-specific include mismatches and divergence between raw and paravirt lock semantics. Test signals include RT kernel builds, locktorture, lockdep, and paravirt guest contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h -->
