<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h

Purpose: customizes queued spinlock behavior for LoongArch and selects architecture paravirtualization hooks when available.
Important APIs and types: includes generic qspinlock definitions, architecture atomic/cmpxchg primitives, and paravirt qspinlock support under the relevant configuration. It exposes the spinlock operations expected by generic locking code.
Control flow: locking flow is delegated to the generic queued spinlock implementation, with LoongArch atomic operations providing acquisition/release ordering and optional PV substitutions.
State and persistence: spinlock state lives in `qspinlock` words owned by callers; this header does not hold global state.
Dependencies and integration: integrates with `asm/cmpxchg.h`, `asm-generic/qspinlock.h`, `asm/paravirt.h`, scheduler/preemption locking, and SMP memory ordering.
Risks and test signals: atomic ordering mistakes show up as deadlocks or data races under SMP. Signals include locktorture, qspinlock selftests, KCSAN/lockdep, and virtualized guest spinlock benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h -->
