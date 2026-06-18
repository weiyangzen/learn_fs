<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h

Purpose: declares LoongArch SMP CPU mapping, boot, IPI, and hotplug interfaces.
Important APIs and types: exposes logical/physical CPU maps, `cpu_logical_map`, `cpu_number_map`, `loongson_send_ipi_*`, `show_ipi_list`, `start_secondary`, `smp_prepare_*`, `smp_send_stop`, and boot data for secondary CPUs.
Control flow: boot code maps physical CPU IDs from ACPI/FDT, starts secondaries with stack/thread info, and uses IPI helpers for reschedule, call-function, and stop events.
State and persistence: CPU maps and boot data persist per-system CPU topology and handoff state for secondary startup.
Dependencies and integration: integrates with ACPI MADT parsing, topology, irqchip/IPI controllers, scheduler SMP code, CPU hotplug, and `head.S` `smpboot_entry`.
Risks and test signals: CPU ID map corruption causes wrong IPI targets or hotplug failures. Signals include SMP boot, CPU online/offline, scheduler IPIs, kexec crash stop, and topology tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h -->
