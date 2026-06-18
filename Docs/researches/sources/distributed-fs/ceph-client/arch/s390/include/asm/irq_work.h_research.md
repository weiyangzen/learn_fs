# sources/distributed-fs/ceph-client/arch/s390/include/asm/irq_work.h

Purpose: This header tells generic irq_work that s390 can raise an interrupt for queued irq_work.

Important APIs/types/functions: `arch_irq_work_has_interrupt()` always returns true.

Control flow: Generic irq_work code uses this predicate to decide that queued work can be kicked asynchronously instead of relying only on polling or timer fallback.

State and persistence: There is no header-owned state.

Dependencies and integration points: It integrates generic irq_work with the s390 external-interrupt mechanism.

Risks and test signals: If interrupt delivery is broken, irq_work users can stall. Tests include irq_work selftests, scheduler/perf users that queue irq_work from hardirq/NMI-like contexts, and CPU hotplug.
