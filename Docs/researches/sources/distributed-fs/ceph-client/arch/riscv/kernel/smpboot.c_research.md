<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c

Purpose: Discovers and starts secondary RISC-V CPUs from device tree or ACPI, prepares SMP boot, and handles secondary CPU entry into the scheduler.

Important APIs/types/functions: Provides `smp_prepare_cpus()`, ACPI RINTC parser, DT CPU parser, `setup_smp()`, `start_secondary_cpu()`, `arch_cpuhp_kick_ap_alive()`, `__cpu_up()`, `smp_cpus_done()`, and `smp_callin()`.

Control flow: Boot parses CPU topology, records hart IDs, skips disabled or invalid CPUs, and initializes CPU operations. CPU bring-up starts the target hart through its CPU ops, waits for `cpu_running`, and secondary entry initializes traps, timers, vector size, MMU/cache state, interrupt handling, and CPU online state before idle.

State and persistence: Maintains `cpu_running` completion, `cpu_count`, CPU maps, and per-CPU hart mappings created during enumeration.

Dependencies and integration points: Depends on firmware CPU ops, SBI/HSM or platform boot methods, DT/ACPI topology, `smp.c` IPI mapping, CPU hotplug, and per-CPU architecture init.

Risks: Duplicate or missing hart IDs break logical CPU mapping. Bring-up timeout leaves CPUs offline. Secondary initialization ordering must install traps/timers before enabling normal scheduling.

Test signals: DT and ACPI SMP boot, disabled CPU nodes, CPU hotplug online/offline, systems with non-contiguous hart IDs, and failure injection in CPU start ops.

Source read size: 264 lines, 5663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c -->
