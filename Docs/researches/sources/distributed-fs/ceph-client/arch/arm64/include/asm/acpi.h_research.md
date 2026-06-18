## sources/distributed-fs/ceph-client/arch/arm64/include/asm/acpi.h

### Purpose
Defines ARM64 ACPI integration hooks, MADT validation helpers, CPU idle context flags, ACPI enable/disable helpers, NUMA hooks, and APEI attributes.

### Important APIs, Types, And Functions
Important macros include `ACPI_MADT_GICC_MIN_LENGTH`, `BAD_MADT_GICC_ENTRY`, `ACPI_MADT_GICC_SPE`, `ACPI_MADT_GICC_TRBE`, `CPUIDLE_*`, `PHYS_CPUID_INVALID`, `cpu_physical_id`, and `ACPI_TABLE_UPGRADE_MAX_PHYS`. Functions/prototypes include `arch_get_idle_state_flags`, `disable_acpi`, `enable_acpi`, `acpi_cpu_get_madt_gicc`, `get_cpu_for_acpi_id`, `acpi_init_cpus`, `apei_claim_sea`, `acpi_parking_protocol_valid`, `acpi_set_mailbox_entry`, `acpi_get_enable_method`, and NUMA helpers.

### Control Flow
Most behavior is inline and configuration-selected. ACPI enable/disable toggles global ACPI/PCI/IRQ flags. CPU init paths query MADT, PSCI, and parking protocol support. Idle code maps ACPI architecture context-loss flags to cpuidle flags. APEI and NUMA hooks dispatch to real implementations only when enabled.

### State, Persistence, And Dependencies
State is global kernel ACPI flags and CPU maps maintained elsewhere. Dependencies include cpuidle, EFI, memblock, PSCI, cputype, I/O mapping, ptrace, SMP platform, and TLB flush headers.

### Integration Points
Used by ARM64 ACPI boot, CPU discovery, idle, error reporting, NUMA, and table upgrade code.

### Risks
MADT length checks must match ACPI revisions; incorrect enable-method logic can prevent CPU bring-up; global ACPI flags affect boot-wide behavior; NUMA fallback values must be safe for non-NUMA builds.

### Test Signals
Boot ACPI ARM64 systems with PSCI and parking protocol, validate MADT parsing and GICC optional fields, run kdump CPU mapping, APEI SEA injection, NUMA initialization, and DT-only builds where ACPI stubs compile.
