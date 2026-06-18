<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c` implements arm64 ACPI boot enablement, FADT validation, table mapping, PSCI detection, ACPI memory mapping attributes, SEA handling, memory reservation, and CPU UID mapping. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`; types: `acpi_table_header`, `acpi_table_fadt`, `acpi_madt_generic_interrupt`, `acpi_table_facs`, `pt_regs`; functions/prototypes/exports: `parse_acpi`, `dt_is_stub`, `__acpi_unmap_table`, `acpi_psci_present`, `acpi_psci_use_hvc`, `acpi_fadt_sanity_check`, `acpi_boot_table_init`, `__acpi_get_writethrough_mem_attribute`, `__acpi_get_mem_attribute`, `apei_claim_sea`, `arch_reserve_mem_area`, `acpi_map_cpu`, `acpi_unmap_cpu`, `acpi_get_cpu_uid`, `get_cpu_for_acpi_id`, `acpi_disabled`, `acpi_pci_disabled`. The file is 490 lines / 13059 bytes. Direct includes are `linux/acpi.h`, `linux/arm-smccc.h`, `linux/cpumask.h`, `linux/efi.h`, `linux/efi-bgrt.h`, `linux/init.h`, `linux/irq.h`, `linux/irqdomain.h`, `linux/irq_work.h`, `linux/memblock.h`, `linux/of_fdt.h`, `linux/libfdt.h`, `linux/smp.h`, `linux/serial_core.h`, `linux/suspend.h`, `linux/pgtable.h`, `acpi/ghes.h`, `acpi/processor.h`, `asm/cputype.h`, `asm/cpu_ops.h`, `asm/daifflags.h`, `asm/smp_plat.h`.

### Control Flow
`parse_acpi` records boot parameters, `acpi_boot_table_init` arbitrates ACPI versus DT and validates the FADT, `acpi_os_ioremap` maps ACPI-described memory with attribute selection, and CPU helpers map MADT processor identifiers to logical CPUs.

### State, Persistence, And Dependencies
Notable global/static state symbols are `acpi_noirq`, `acpi_disabled`, `acpi_pci_disabled`, `param_acpi_off`, `param_acpi_on`, `param_acpi_force`, `param_acpi_nospcr`, `__init`, `node`, `acpi_psci_use_hvc`, `ret`, `attr`, `end`, `apei_claim_sea`, `err`, `return_to_irqs_enabled`, `acpi_map_cpu`, `acpi_unmap_cpu`, and 3 more. Global ACPI enable flags, boot parameters, FADT-derived PSCI state, memblock reservations, and ACPI processor mappings persist after boot. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
ACPI/DT arbitration mistakes, unsafe memory attributes, bad PSCI conduit detection, or incorrect ACPI CPU IDs can break boot, CPU hotplug, PCI/IRQ setup, or firmware error handling.

### Test Signals
Boot with `acpi=off`, `on`, and `force`; validate FADT/SPCR/MADT tables, GHES SEA handling, CPU mapping, memblock reservations, and ACPI ioremap attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/acpi.c -->
