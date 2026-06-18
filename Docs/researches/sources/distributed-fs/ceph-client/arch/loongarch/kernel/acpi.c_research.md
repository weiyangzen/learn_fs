<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c

Purpose: implements LoongArch ACPI boot-table parsing, CPU discovery, NUMA affinity, hotplug mapping, and architecture ACPI memory mapping.
Important APIs and types: defines `acpi_disabled`, `acpi_noirq`, `acpi_pci_disabled`, `acpi_strict`, `num_processors`, `disabled_cpus`, `acpi_core_pic`, `__acpi_map_table`, `acpi_os_ioremap`, MADT parsers, `parse_acpi_topology`, `acpi_boot_table_init`, SRAT affinity handlers, `arch_reserve_mem_area`, CPU hotplug map/unmap, and `acpi_get_cpu_uid`.
Control flow: early boot initializes ACPI tables, records boot CPU ID, parses MADT in two passes for enabled/disabled CPUs, parses EIO PIC masters, optionally parses SPCR/BGRT, and falls back to FDT earlycon if ACPI is disabled or table init fails. NUMA callbacks map proximity domains to CPU IDs; hotplug updates present masks and node mappings.
State and persistence: stores CPU presence/possible maps, physical/logical CPU maps, MADT core PIC entries, topology/core IDs, NUMA mappings, processor counts, and ACPI suspend low-level hook.
Dependencies and integration: depends on ACPI core, memblock/early ioremap, serial SPCR, EFI BGRT, irqdomain, Loongson sysconf, NUMA helpers, SMP CPU maps, and CPU hotplug.
Risks and test signals: BIOS table quirks directly affect CPU enumeration and topology. Signals include ACPI boot, FDT fallback, CPU hotplug, NUMA SRAT/PPTT validation, early console, BGRT/sysfb, and suspend builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c -->
