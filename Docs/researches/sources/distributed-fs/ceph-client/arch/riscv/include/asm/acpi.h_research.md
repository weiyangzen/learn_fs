<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h

## Purpose
Defines RISC-V ACPI architecture interfaces and stubs.

## Important APIs, Types, And Functions
For `CONFIG_ACPI`, it defines `phys_cpuid_t`, `PHYS_CPUID_INVALID`, `acpi_os_ioremap`, `acpi_strict`, ACPI disable/enable helpers, `cpu_physical_id`, `acpi_has_cpu_in_madt()`, `arch_fix_phys_package_id()`, RINTC mapping APIs, ISA extraction, and CBO block-size extraction. Without ACPI, it provides no-op or `-EINVAL` stubs. It also declares `acpi_map_cpus_to_nodes()` when ACPI NUMA is enabled.

## Control Flow
ACPI core and RISC-V setup code use these helpers to map firmware CPU IDs to harts, control ACPI availability, map ACPI tables, parse RISC-V ISA data, and get cache-block operation sizes.

## State And Persistence
Persistent state is global ACPI enable/disable flags and CPU/hart/NUMA mappings maintained by implementation files.

## Dependencies And Integration Points
Integrated with ACPI MADT/RINTC parsing, RISC-V hart ID maps, PCI/IRQ disable flags, CBO extension setup, and ACPI NUMA.

## Risks And Edge Cases
ACPI on RISC-V is strict; out-of-spec workarounds are disabled. Bad CPU mapping or ISA parsing can break boot CPU enumeration, interrupt routing, or extension detection.

## Test Signals
Signals are ACPI boot on RISC-V platforms, MADT RINTC CPU discovery, ACPI NUMA node mapping, ISA/CBO table parsing, and non-ACPI builds compiling through stubs.

Source read size: 95 lines, 2460 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h -->
