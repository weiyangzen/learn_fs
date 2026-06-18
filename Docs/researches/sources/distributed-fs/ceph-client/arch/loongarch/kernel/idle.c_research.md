<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c

Purpose: exposes the LoongArch CPU idle routine to generic idle code.
Important APIs and types: calls the assembly `__arch_cpu_idle` implementation through architecture idle hooks.
Control flow: scheduler idle loop invokes the arch idle function; assembly enables interrupts and executes the LoongArch idle instruction with a protected interrupt window.
State and persistence: no long-lived state; CPU enters and leaves low-power idle state.
Dependencies and integration: integrates with `genex.S` idle interrupt handling, scheduler idle loop, IRQ state, and CPU power management.
Risks and test signals: incorrect interrupt enable ordering can miss reschedules. Signals include idle/reschedule stress, timer interrupts, cpuidle tracing, and suspend-adjacent tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c -->
