## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq_work.h

Purpose: tells generic irq_work whether arm64 can raise interrupt-backed irq_work.

Important APIs/types/functions: defines `arch_irq_work_has_interrupt()` returning true.

Control flow: generic irq_work uses this predicate to decide if queued work can be kicked by an interrupt.

State and persistence: no state in this header.

Dependencies and integration: used by irq_work, scheduler, perf, and RCU callbacks needing interrupt context execution.

Risks: incorrect return value changes latency or deadlock assumptions. Test signals are irq_work selftests, perf event delivery, RCU stall tests, and scheduler nohz coverage.
