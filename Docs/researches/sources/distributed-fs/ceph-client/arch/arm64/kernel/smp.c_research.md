## sources/distributed-fs/ceph-client/arch/arm64/kernel/smp.c

### Purpose
`smp.c` is the ARM64 SMP bring-up, CPU hotplug, IPI, panic-stop, and CPU enumeration implementation. It maps firmware-described CPUs to logical IDs, starts secondary CPUs through `cpu_operations`, enables per-CPU interrupt/timer state, and implements architecture callbacks used by generic scheduler, hotplug, IRQ, kgdb, kexec, and watchdog code.

### Important APIs, Types, And Functions
Important exported or architecture entry points include `__cpu_up`, `secondary_start_kernel`, `__cpu_disable`, `arch_cpuhp_cleanup_dead_cpu`, `cpu_die`, `cpu_die_early`, `smp_cpus_done`, `smp_prepare_boot_cpu`, `arch_register_cpu`, `acpi_cpu_get_madt_gicc`, `smp_init_cpus`, `smp_prepare_cpus`, `arch_show_interrupts`, IPI send helpers, `set_smp_ipi_range_percpu`, `smp_send_stop`, `crash_smp_send_stop`, `smp_crash_stop_failed`, and `cpus_are_stuck_in_kernel`.

### Control Flow
Boot CPU setup records boot CPU features and per-CPU offset. Early enumeration walks DT or ACPI MADT, rejects invalid or duplicate MPIDRs, initializes `cpu_ops`, and marks possible CPUs. Preparation calls each CPU's `cpu_prepare` and marks present CPUs. `__cpu_up` publishes the idle task in `secondary_data`, asks firmware/platform `cpu_boot` to release the CPU, and waits for `cpu_running`. `secondary_start_kernel` switches to `init_mm`, uninstalls the idmap, validates capabilities, runs `cpu_postboot`, stores CPU info/topology, starts per-CPU IRQ/timer notifiers, sets online, completes the boot waiter, restores DAIF, and enters idle. Hot-unplug validates `cpu_die`, removes topology/NUMA state, tears down IPIs, migrates IRQs, reports dead, and calls firmware to power down.

### State, Persistence, And Dependencies
State includes `secondary_data`, `cpu_logical_map`, possible/present/online masks, `cpu_madt_gicc`, `cpu_count`, `bootcpu_valid`, per-CPU IPI descriptors, `ipi_irq_base`, `nr_ipi`, `percpu_ipi_descs`, `crash_stop`, `cpus_stuck_in_kernel`, topology and NUMA data. There is no filesystem persistence; state is CPU masks, firmware-visible release protocol state, interrupt descriptors, and boot status words.

### Integration Points
The file connects generic SMP and CPU hotplug core to ARM64 `cpu_ops`, DT/ACPI CPU description, GIC SGI/LPI IPIs, pseudo-NMI support, irq_work, scheduler IPIs, tick broadcast, kgdb roundup, kexec crash saving, SDEI masking, KVM hyp layout setup, topology, NUMA, and feature finalization.

### Risks
CPU bring-up can fail silently if boot status, MPIDR mapping, cache visibility, or firmware release methods drift. IPI setup must match SGI versus per-CPU LPI delivery and pseudo-NMI state. Panic stop paths intentionally run with limited locking and can race CPU hotplug. Hotplug shutdown relies on firmware actually leaving kernel text before resources are reused.

### Test Signals
Run DT and ACPI boots, maxcpus/nosmp, CPU online/offline loops, IPI stress, irq_work and tick broadcast tests, kgdb roundup, panic/kexec crash paths, pseudo-NMI stop retry paths, and KVM-enabled EL1/EL2 boots.
