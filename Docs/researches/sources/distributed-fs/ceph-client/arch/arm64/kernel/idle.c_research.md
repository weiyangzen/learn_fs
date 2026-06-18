# sources/distributed-fs/ceph-client/arch/arm64/kernel/idle.c

Purpose: Provides the default low-level arm64 idle path around `wfi`.

Important APIs: `cpu_do_idle()` saves interrupt-priority masking context, executes `dsb(sy)` and `wfi`, then restores the context. `arch_cpu_idle()` delegates to `cpu_do_idle()`.

Control flow and state: no persistent state is stored in this file. The temporary `arm_cpuidle_irq_context` preserves interrupt controller priority masking state so a CPU using priority masking can still wake from interrupts.

Dependencies and integration: integrates with the generic idle loop, arm64 cpuidle helpers, IRQ flags, barrier semantics, cpufeature/sysreg support, and any platform cpuidle driver that falls back to the arch default idle handler.

Risks and test signals: risks are failing to unmask the wake signal in PMR-backed interrupt priority masking or missing the barrier before WFI. Test with idle loop stress, tickless idle, systems using GIC priority masking, suspend-to-idle, and interrupt wake latency checks.
