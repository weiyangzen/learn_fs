## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpuidle.h

Purpose: declares arm64 CPU idle entry points and PSCI idle-state helpers.

Important APIs/types/functions: provides `cpu_do_idle`, `cpu_do_idle_irqprio`, `cpu_suspend`, `arm_cpuidle_init`, and PSCI CPU suspend parameter helpers when PSCI CPU idle is enabled.

Control flow: idle code enters WFI-like low-power states, with special handling when IRQ priority masking is active. PSCI helpers encode firmware suspend state parameters.

State and persistence: no durable state in this header; CPU idle drivers and firmware manage idle state.

Dependencies and integration: integrates cpuidle, PSCI firmware, CPU suspend, IRQ priority masking, and scheduler idle.

Risks: wrong entry path can leave interrupts masked or choose invalid firmware states. Test signals are cpuidle residency, suspend/resume, interrupt wakeups, and PSCI idle-state validation.
