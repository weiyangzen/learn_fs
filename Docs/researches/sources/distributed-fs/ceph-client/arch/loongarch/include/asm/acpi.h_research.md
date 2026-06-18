# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acpi.h

## Purpose

`acpi.h` declares LoongArch ACPI integration helpers and constants for MADT CPU discovery, wakeup address handling, and ACPI table upgrade limits. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `disable_acpi`, `acpi_has_cpu_in_madt`, `acpi_get_wakeup_address`, `acpi_os_ioremap`, `MAX_CORE_PIC`, and `struct acpi_madt_core_pic` references. Concrete declarations observed in the file: Includes: `asm/smp.h`, `asm/suspend.h`. Macros: `_ASM_LOONGARCH_ACPI_H`, `acpi_os_ioremap`, `MAX_CORE_PIC`, `ACPI_TABLE_UPGRADE_MAX_PHYS`. Types referenced or declared: `list_head`, `acpi_madt_core_pic`. Functions/syscalls: `disable_acpi`, `acpi_has_cpu_in_madt`, `acpi_get_wakeup_address`.

## Control Flow, State, And Persistence

Runtime flow is elsewhere; this header supplies prototypes and constants used during ACPI boot, CPU enumeration, suspend, and ioremap.

## Dependencies And Integration Points

It integrates with SMP, suspend, ACPI MADT parsing, and generic ACPI OS services.

## Risks And Test Signals

Risks are CPU discovery mismatch, wake address errors, and incorrect table-upgrade physical limits. Test signals are ACPI boot logs, CPU enumeration, suspend/resume, and MADT parsing tests.
 A local static signal for this file is that it has 59 lines and 1293 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
