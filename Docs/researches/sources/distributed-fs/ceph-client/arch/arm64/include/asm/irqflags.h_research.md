## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irqflags.h

Purpose: implements generic local IRQ flag operations for arm64, supporting both DAIF masking and GIC priority masking.

Important APIs/types/functions: exports `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_save`, and `arch_local_irq_restore`, with DAIF and PMR internal variants.

Control flow: each public helper checks `system_uses_irq_prio_masking()`. DAIF paths write `daifset/daifclr` or restore DAIF; PMR paths read/write `ICC_PMR_EL1`, validate debug-priority states, and call `pmr_sync` where required.

State and persistence: modifies CPU-local DAIF/PSTATE or interrupt-controller PMR state.

Dependencies and integration: depends on barrier, ptrace PSR bits, sysreg, cpufeature, GIC priority constants, and pseudo-NMI support.

Risks: wrong save/restore semantics can enable interrupts in critical sections or block them permanently. Test signals are lockdep IRQ tracing, pseudo-NMI tests, interrupt storm stress, preempt/RT tests, and GIC priority masking debug checks.
