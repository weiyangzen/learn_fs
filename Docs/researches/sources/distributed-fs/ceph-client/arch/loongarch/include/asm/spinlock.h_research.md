<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h

Purpose: selects LoongArch spinlock implementation by including queued spinlock support.
Important APIs and types: includes `asm/qspinlock.h` and generic queued read-write locks as required by the kernel locking API.
Control flow: runtime locking behavior is implemented by included generic and architecture atomic code.
State and persistence: lock state is caller-owned; this file only wires type/operation selection.
Dependencies and integration: integrates with SMP atomic primitives, lockdep, scheduler, interrupt paths, and paravirtualized locking when enabled.
Risks and test signals: inclusion/order errors break low-level locking builds. Signals include allmodconfig, locktorture, lockdep, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h -->
