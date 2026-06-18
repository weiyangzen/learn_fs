# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcr.h

Purpose: Performance Control Register abstraction for sparc64 performance counters and NMI overflow programming across Niagara-era PCR layouts.

Important APIs/types/functions: types `pcr_ops`; functions/helpers `deferred_pcr_work_irq`, `schedule_deferred_pcr_work`, `pcr_arch_init`; macros/constants `__PCR_H`, `PCR_PIC_PRIV`, `PCR_STRACE`, `PCR_UTRACE`, `PCR_N2_HTRACE`, `PCR_N2_TOE_OV0`, `PCR_N2_TOE_OV1`, `PCR_N2_MASK0`, `PCR_N2_MASK0_SHIFT`, `PCR_N2_SL0`, `PCR_N2_SL0_SHIFT`, `PCR_N2_OV0`, `PCR_N2_MASK1`, `PCR_N2_MASK1_SHIFT`, `PCR_N2_SL1`, `PCR_N2_SL1_SHIFT`, `PCR_N2_OV1`, `PCR_N4_OV`, plus 11 more.

Control flow: The file is driven by preprocessor gates such as `__PCR_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: The global `pcr_ops` vtable persists the selected CPU implementation; deferred PCR work reschedules counter handling out of constrained interrupt contexts.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Perf-event PMU tests, NMI overflow delivery, deferred IRQ work, and N2/N4 event mask programming are the main test signals.
