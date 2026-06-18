<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c

## Purpose
Implements Xen PV `smp_ops` for x86. It prepares PV CPU topology, initializes per-CPU vCPU state and event channels, builds the Xen vCPU guest context for secondary CPUs, brings CPUs up/down through Xen `VCPUOP_*`, and wires PV-specific IRQ-work and PMU interrupts.

## Important APIs, Types, And Functions
Important state is `xen_cpu_initialized_map`, `xen_irq_work`, and `xen_pmu_irq`. Key functions include `cpu_bringup_and_idle`, `xen_smp_intr_init_pv`, `xen_smp_intr_free_pv`, `xen_pv_smp_prepare_boot_cpu`, `xen_pv_smp_prepare_cpus`, `cpu_initialize_context`, `xen_pv_kick_ap`, CPU hotplug callbacks, `xen_smp_count_cpus`, and `xen_smp_init`.

## Control Flow
Early setup installs PV `smp_ops` and suppresses BIOS MP table parsing. Boot CPU preparation makes the old GDT writable if needed, places vCPU info, and enables PV spinlock patching. CPU preparation initializes CPU0 locks, common SMP state, speculative-store-bypass topology, PMU, common/PV interrupts, and the initialized CPU mask. Secondary bringup runs `common_cpu_up`, sets runstate info, masks event upcalls, builds a `vcpu_guest_context` with GDT, trap callbacks, stack, CR3, and per-CPU base, calls `VCPUOP_initialise`, initializes PMU, then calls `VCPUOP_up`.

## State And Persistence
State includes CPU-present/possible masks, Xen initialized CPU mask, per-CPU IRQ bindings, readonly GDT pages, per-CPU CR3, per-CPU PMU pages, and vCPU runstate/timer/event-channel state. CPU teardown frees IRQs, locks, timers, and PMU pages.

## Dependencies And Integration Points
Depends on Xen vCPU, event, PMU, and page APIs; x86 descriptor, CPU, APIC, paravirt, and speculation setup; common Xen SMP code; Xen time code; and assembly entry points `asm_cpu_bringup_and_idle` and `xen_cpu_bringup_again`.

## Risks And Edge Cases
`cpu_initialize_context` is sensitive to descriptor alignment, readonly GDT handling, stack pointer placement, callback EIPs, and pfn-to-cr3 conversion. `nosmp` and `noapic` are fatal under PV. CPU0 cannot be hot-unplugged. PMU IRQ setup depends on global `is_xen_pmu`. Several hypercall failures are `BUG_ON`.

## Test Signals
Signals include PV boot with multiple vCPUs, CPU online/offline stress, `/proc/interrupts` for IRQ_WORK and PMU, successful function-call IPIs, PMU sampling, stop-other-CPUs behavior on shutdown, and boot tests with dom0/domU topology differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c -->
