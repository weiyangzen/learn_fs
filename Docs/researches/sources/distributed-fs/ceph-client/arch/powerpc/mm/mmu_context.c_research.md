# sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_context.c

Purpose: implements the common context-switch wrapper `switch_mm_irqs_off()` and non-Book3S64 mmap-exit cleanup.

Important APIs and control flow: the switch path marks the target `mm` active on the current CPU, increments active CPU accounting, issues a full barrier that pairs with TLB invalidation, updates subarchitecture PGD/PID tracking in the task or PACA, stops Altivec streams, calls membarrier handling when appropriate, and delegates hardware context switching to `switch_mmu_context()`. Non-Book3S64 `arch_exit_mmap()` frees stored PTE fragments.

State and dependencies: state touched includes `mm_cpumask`, `mm->context.active_cpus`, task thread PGD/SR/PID fields, PACA PGD, and PTE fragments. It depends on CPU hotplug-safe current CPU IDs, Altivec feature flags, membarrier, and subarch `switch_mmu_context()`. Risks are missing memory barriers causing stale TLB entries after PTE clearing, incorrect active CPU counts, and PGD/PID tracking mismatches on KUAP BookE. Test signals include context-switch stress, membarrier tests, lazy TLB/mm teardown tests, and PPC32/Book3E64 configurations.
