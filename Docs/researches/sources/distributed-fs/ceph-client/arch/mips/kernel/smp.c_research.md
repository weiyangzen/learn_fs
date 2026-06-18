## sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c` is the generic MIPS SMP core. It maintains CPU topology maps, registers platform SMP operations, allocates generic IPI IRQs, runs secondary CPU startup, implements stop and hotplug glue, and provides SMP-aware TLB shootdown routines.

### Important APIs, Types, And Functions
Global maps include `__cpu_number_map`, `__cpu_logical_map`, `smp_num_siblings`, `cpu_sibling_map`, `cpu_core_map`, `cpu_foreign_map`, `cpu_coherent_mask`, and `__cpu_primary_thread_mask`. Important functions include `register_smp_ops()`, `mips_smp_send_ipi_single()`, `mips_smp_send_ipi_mask()`, `mips_smp_ipi_allocate()`, `mips_smp_ipi_free()`, `start_secondary()`, `smp_prepare_cpus()`, `smp_prepare_boot_cpu()`, `__cpu_up()` or `arch_cpuhp_kick_ap_alive()`, TLB flush entry points, and `tick_broadcast()`.

### Control Flow
Boot CPU setup records CPU0 online and possible, then `smp_prepare_cpus()` initializes boot mm context, calls platform `prepare_cpus`, builds sibling/core maps, and initializes coherent masks. `start_secondary()` probes CPU state, installs traps, initializes clockevents and MAARs, calls platform secondary hooks, calibrates delay, updates topology, synchronizes Count registers, marks the CPU online, and enters idle. Generic IPI allocation finds an IPI irqdomain and reserves call and reschedule IRQs. TLB flushes choose between MMID/GINV global invalidation, IPIs to other CPUs, ASID context invalidation, and local flushes depending on CPU capability and mm sharing.

### State, Persistence, And Dependencies
State is in global CPU maps, IRQ descriptors for call/reschedule IPIs, completions for AP startup, per-CPU call-single data for tick broadcast, and mm ASID context arrays. Dependencies include `asm/mips-cps.h`, `asm/ginvt.h`, `asm/mmu_context.h`, `asm/time.h`, `asm/maar.h`, irq domains, OF IRQ lookup, CPU hotplug, and generic TLB/cache primitives.

### Integration Points
Platform files such as `smp-cps.c`, `smp-mt.c`, `smp-bmips.c`, and `smp-up.c` register `mp_ops`. Trap initialization, timer initialization, count synchronization, scheduler IPIs, generic `smp_call_function`, CPU hotplug, and MM/TLB code all converge here.

### Risks
Topology map correctness affects scheduling, IPI fanout, and TLB shootdown. IPI domain handling must degrade safely on true UP systems and fail on broken multi-CPU configurations. Secondary startup completion ordering protects the boot CPU from proceeding before counter sync and online marking. TLB flush paths are architecture-sensitive: MMID/GINV, ASID invalidation, executable VMA icache assumptions, and preemption boundaries must remain correct.

### Test Signals
Test CPU bring-up, CPU hotplug, call-function and reschedule IPIs, `nosmt` and `smt=N`, TLB flushes for single-threaded and multithreaded mms, executable VMA invalidation, kernel range flushes, MMID-capable systems, GINV-capable systems, and tick broadcast on broadcast-clockevent configurations.
