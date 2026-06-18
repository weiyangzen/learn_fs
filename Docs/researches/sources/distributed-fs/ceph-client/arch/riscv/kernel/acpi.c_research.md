<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c

Purpose: Implements RISC-V low-level ACPI boot support, table initialization, FADT validation, RINTC MADT caching, ACPI table mapping, ACPI ioremap policy, PCI config access, and CPU UID lookup.

Important APIs/types/functions: Key functions are `parse_acpi()`, `acpi_boot_table_init()`, `acpi_init_rintc_map()`, `acpi_cpu_get_madt_rintc()`, `__acpi_map_table()`, `__acpi_unmap_table()`, `acpi_os_ioremap()`, `raw_pci_read()`, `raw_pci_write()`, and `acpi_get_cpu_uid()`.

Control flow: Early `acpi=` parameters decide whether to disable, prefer, or force ACPI. Boot initialization enables ACPI, parses tables, checks FADT revision/HW-reduced mode, parses SPCR/BGRT, caches enabled MADT RINTC entries by CPU, and maps AML/ACPI physical regions with EFI/memblock-aware protections.

State and persistence: Persistent state includes `acpi_disabled`, `acpi_noirq`, `acpi_pci_disabled`, command-line booleans, and `cpu_madt_rintc[NR_CPUS]`.

Dependencies and integration points: Integrates with EFI, memblock, early remap, ACPI core, MADT/RINTC, SPCR early console, BGRT, PCI, and RISC-V hart-to-CPU mapping.

Risks: Bad ACPI enable policy or ioremap protections can boot the wrong firmware path, expose kernel memory to AML mappings, or lose CPU UID/RINTC data.

Test signals: ACPI and DT boot matrix, `acpi=off/on/force`, invalid FADT tests, SPCR early console, ACPI PCI config access, MADT RINTC CPU mapping, and EFI memory map edge cases.

Source read size: 355 lines, 9593 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c -->
