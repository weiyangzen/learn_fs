## sources/distributed-fs/ceph-client/arch/loongarch/kernel/smp.c

### Purpose
`smp.c` implements LoongArch SMP topology, IPI delivery, secondary CPU boot, CPU hotplug/dead loops, PM IPI restore, boot CPU preparation, stop-IPIs, and cross-CPU TLB shootdowns. It connects firmware CPU maps to Linux logical CPUs and manages sibling/core/LLC masks.

### Important APIs, Types, And Functions
Global maps include `__cpu_number_map`, `__cpu_logical_map`, `cpu_sibling_map`, `cpu_llc_shared_map`, `cpu_core_map`, `cpu_foreign_map`, `cpuboot_data`, and `mp_ops`. Key functions include `show_ipi_list`, `calculate_cpu_foreign_map`, `loongson_smp_setup`, `loongson_prepare_cpus`, `loongson_boot_secondary`, `loongson_init_secondary`, `loongson_smp_finish`, `smp_prepare_boot_cpu`, `smp_prepare_cpus`, `__cpu_up`, `start_secondary`, `smp_send_stop`, and the `flush_tlb_*` family.

### Control Flow
FDT setup maps hardware CPU IDs to logical IDs and initializes node state. Prepare paths parse ACPI topology, clear mailboxes, mark boot CPU online, set sibling/LLC/core masks, and enable paravirt hooks. Booting a secondary writes the physical entry address to mailbox 0 and sends `ACTION_BOOT_CPU`; the secondary syncs counters, sets per-CPU offset, probes CPU, initializes timer/IPI state, marks itself online, signals completions, enables IRQs, and enters the idle loop. TLB shootdowns either call remote CPUs via masks or clear stale `cpu_context` entries when the mm is local-only.

### State, Persistence, And Dependencies
Persistent state includes CPU maps, topology masks, per-CPU online/hotplug state, IOCSR mailbox/IPI registers, and mm context generation per CPU. Dependencies include ACPI/PPTT topology, OF CPU nodes, Loongson IOCSR IPI/mailbox registers, paravirt IPI hooks, timer sync, cpuhp, IRQ migration, and TLB local flush primitives.

### Integration Points
Generic SMP calls architecture prepare/boot/start/stop hooks. `/proc/interrupts` uses `show_ipi_list`. NUMA code consumes CPU maps. Paravirt may replace `mp_ops`. MM code calls `flush_tlb_all/mm/range/kernel_range/page/one`.

### Risks
CPU logical/physical maps must be initialized before IPIs and mailbox sends. Completion reuse in CPU bring-up assumes serialized CPU-up operations. Hotplug rejects I/O master CPUs and must migrate IRQs before disabling masks. TLB shootdown optimizations that skip remote IPIs rely on accurate `mm_users`, `current->mm`, and `cpu_context` state.

### Test Signals
Boot SMP via ACPI and FDT, CPU hotplug online/offline, hibernation nonboot CPU disable, paravirt and native IPIs, `/proc/interrupts` IPI counters, stop/reboot paths, and mm stress tests that exercise all TLB flush variants across multiple CPUs.
