## sources/distributed-fs/ceph-client/drivers/acpi/processor_core.c

### Purpose
`processor_core.c` maps ACPI processor namespace identifiers to kernel CPU identifiers and physical CPU IDs by reading `_MAT` objects and MADT subtables. It also provides optional IOAPIC hotplug lookup support when `CONFIG_ACPI_HOTPLUG_IOAPIC` is enabled.

### Important APIs, Types, And Functions
The central exported APIs are `acpi_get_phys_id()`, `acpi_map_cpuid()`, and `acpi_get_cpuid()`. Early boot helpers include `acpi_map_madt_entry()` and `acpi_get_madt_revision()`. Static mapper functions decode architecture-specific MADT records: local APIC, x2APIC, SAPIC, ARM GICC MPIDR, RISC-V RINTC hart ID, and LoongArch CORE_PIC. `get_madt_table()` caches a runtime MADT mapping.

### Control Flow
CPU mapping first evaluates a processor object's `_MAT`; if it yields a recognized local interrupt-controller subtable, the file extracts the hardware ID from that subtable. If `_MAT` is absent or invalid, it scans the cached MADT. The resulting physical ID is translated to a Linux CPU by matching `cpu_physical_id()` over possible CPUs, with a uniprocessor fallback that accepts only ACPI ID 0 when no physical ID is available. IOAPIC lookup follows the same `_MAT` then MADT fallback for a matching GSI base.

### State, Persistence, And Dependencies
The only retained state is the static cached MADT pointer and read flag. The file depends on ACPICA table APIs, ACPI object evaluation, per-CPU physical-ID helpers, architecture MADT type definitions, and optional IOAPIC hotplug support.

### Integration Points
Processor enumeration, CPU hotplug, architecture setup, and ACPI processor drivers use these helpers to connect namespace `Processor` or processor device objects to kernel CPU numbers. IOAPIC hotplug uses `acpi_get_ioapic_id()` to recover APIC IDs and physical addresses from firmware data.

### Risks
Firmware may provide disabled, malformed, or inconsistent `_MAT` and MADT entries. Runtime MADT caching omits `acpi_put_table()` for the cached pointer, so lifetime assumptions follow ACPI core table mapping behavior. Table scans advance by firmware-provided record lengths and rely on ACPICA table validation. The UP fallback deliberately ignores nonzero ACPI IDs.

### Test Signals
Useful checks include systems with only MADT data, only `_MAT`, disabled processor entries, x2APIC UIDs above and below 255, RISC-V/ARM/LoongArch mappings, UP kernels without SMP tables, and IOAPIC hotplug records with matching and missing GSI bases.
