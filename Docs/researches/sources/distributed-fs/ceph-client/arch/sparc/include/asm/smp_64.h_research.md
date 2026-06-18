# sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_64.h

Purpose: sparc64 SMP header exposing per-CPU id access, scheduler poke, cross-call IPI senders, sibling/core maps, CPU hotplug, global register/PMU snapshots, and tick synchronization.

Important APIs/types/functions: types `seq_file`; functions/helpers `smp_init_cpu_poke`, `scheduler_poke`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `hard_smp_processor_id`, `smp_fill_in_sib_core_maps`, `cpu_play_dead`, `smp_fetch_global_regs`, `smp_fetch_global_pmu`, `smp_bogo`, `smp_info`, `smp_callin`, `cpu_panic`, `smp_synchronize_tick_client`, `smp_capture`, `smp_release`, plus 2 more; macros/constants `_SPARC64_SMP_H`, `raw_smp_processor_id`, `hard_smp_processor_id`, `smp_fill_in_sib_core_maps`, `smp_fetch_global_regs`, `smp_fetch_global_pmu`, `smp_init_cpu_poke`, `scheduler_poke`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SMP_H`, `__ASSEMBLER__`, `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State includes per-CPU `cpu_data`, trap-block CPU ids, global snapshot arrays, CPU sibling masks, and hotplug lifecycle state.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/asi.h`, `asm/starfire.h`, `asm/spitfire.h`, `linux/cpumask.h`, `linux/cache.h`, `linux/bitops.h`, `linux/atomic.h`, `asm/percpu.h`. Integration points include SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps. Test signals: CPU hotplug, scheduler IPI latency, perf snapshot IPIs, sibling maps, tick sync, and suspend/death paths should be tested.
