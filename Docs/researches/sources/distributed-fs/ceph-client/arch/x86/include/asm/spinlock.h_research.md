<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h

Purpose: selects x86 spinlock implementations and architecture hooks. It pulls in queued spinlocks, queued rwlocks, and paravirt variants as configured.

Control flow: generic locking users compile through this header into qspinlock/qrwlock primitives. State is lock object memory. Dependencies include qspinlock, qrwlock, paravirt, and architecture atomic operations.

Risks include config-specific include ordering, lock primitive ABI mismatch, and paravirt locking regressions. Test signals include locktorture, lockdep, SMP stress, RT builds where applicable, and paravirt guest locking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h -->
