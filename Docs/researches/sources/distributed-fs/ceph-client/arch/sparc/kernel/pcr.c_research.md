# sources/distributed-fs/ceph-client/arch/sparc/kernel/pcr.c

## Purpose
Generic sparc64 performance counter register infrastructure for perf, watchdog, and related users. Selects CPU-family `pcr_ops`, negotiates sun4v perf HV APIs, and provides deferred work handling for high-PIL performance counter interrupts.

## Important APIs, Types, and Functions
Exports `pcr_ops`. `deferred_pcr_work_irq()` clears the deferred softint and runs `irq_work`; `arch_irq_work_raise()` raises it. Direct ops read/write `%pcr` and `%pic`, including a Blackbird erratum workaround. N2/N4/N5/M7 ops use direct or HV perf register access. `register_perf_hsvc()` maps chip types to HV groups. `pcr_arch_init()` chooses ops by `tlb_type` and chip type, then calls `nmi_init()`.

## Control Flow
Perf init calls `pcr_arch_init()`. Hypervisor systems register the appropriate HV perf group and choose sun4v ops. Cheetah uses direct ops. Spitfire and unsupported chips return `-ENODEV`. High-priority counter work is deferred through a lower-PIL soft interrupt.

## State and Persistence
Global runtime state includes `pcr_ops` and HV service group/version fields. Hardware PCR/PIC or HV perf registers are modified. No persistence.

## Dependencies and Integration Points
Uses SPARC PIL/NMI/ASI/hypervisor support, irq_work, ftrace, CPU data, PCR bit definitions, `perf_event.c`, and NMI watchdog code.

## Risks and Test Signals
Wrong chip mapping selects incompatible registers. Several HV calls are best-effort. High-PIL context requires deferral. Test via perf PMU init, watchdog/perf counter arbitration, and execution of deferred irq_work.
