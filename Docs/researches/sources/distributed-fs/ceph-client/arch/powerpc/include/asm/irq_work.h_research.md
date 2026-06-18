# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq_work.h

Purpose: Tells generic irq_work that PowerPC has an interrupt mechanism suitable for irq_work callbacks.

Important APIs, types, and functions: Implements `arch_irq_work_has_interrupt()` returning `true`.

Control flow: Generic irq_work uses this predicate to decide that queued work can be raised via an interrupt rather than relying only on timer/context fallback.

State and persistence: No state.

Dependencies and integration points: Integrates generic irq_work with PowerPC interrupt delivery.

Risks: If a platform cannot deliver the expected interrupt, irq_work latency assumptions would be wrong; the architecture declares support globally.

Test signals: Queue irq_work from process, interrupt, and NMI-like contexts; verify prompt execution on SMP and idle CPUs.
