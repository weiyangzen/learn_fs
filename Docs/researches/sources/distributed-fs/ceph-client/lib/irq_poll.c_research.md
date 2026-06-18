# sources/distributed-fs/ceph-client/lib/irq_poll.c

Purpose: implements IRQ polling infrastructure for block-layer style completion polling, analogous to NAPI, using a per-CPU pending list and `IRQ_POLL_SOFTIRQ`.

Important APIs: `irq_poll_init()`, `irq_poll_sched()`, `irq_poll_complete()`, `irq_poll_disable()`, and `irq_poll_enable()`. Internal helpers include `irq_poll_softirq()`, `__irq_poll_complete()`, CPU hotplug migration, and setup via `subsys_initcall`.

Control flow: scheduling checks disabled and scheduled bits, appends the poll object to the current CPU list with interrupts disabled, and raises the softirq. The softirq loops while budget and time remain, invokes `iop->poll(iop, weight)` with interrupts enabled, subtracts work from global budget, and either completes disabled items or rotates still-busy items to the tail. CPU-dead handling splices a dead CPU list into the current CPU and raises the softirq.

State and persistence: state is in `struct irq_poll` bits (`IRQ_POLL_F_SCHED`, `IRQ_POLL_F_DISABLE`), the per-CPU `blk_cpu_iopoll` lists, and the static budget. No persistent storage.

Dependencies and integration: depends on softirq, CPU hotplug, local IRQ control, bitops, and driver-supplied poll callbacks. Block drivers use it to defer interrupt completion work.

Risks: callbacks must obey ownership rules when consuming a full weight; disable spins with sleep until scheduled state is cleared; wrong list manipulation under interrupt state can corrupt per-CPU lists; long callbacks can exhaust softirq budget and require rearming.

Test signals: block driver polling tests, CPU hotplug stress, lockdep/softirq diagnostics, budget exhaustion behavior, and disable/enable races.
