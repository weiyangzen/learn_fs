## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/acpi.c

### Purpose
`compressed/acpi.c` discovers ACPI RSDP early in the compressed kernel and, when KASLR and memory hotremove are enabled, parses SRAT memory affinity subtables to identify immovable memory regions that KASLR should prefer.

### Important APIs, Types, And Functions
Exports are `get_rsdp_addr()`, `count_immovable_mem_regions()`, and `immovable_mem`. Helpers include `__efi_get_rsdp_addr()`, `efi_get_rsdp_addr()`, `compute_checksum()`, `scan_mem_for_rsdp()`, `bios_get_rsdp_addr()`, `get_cmdline_acpi_rsdp()`, and `get_acpi_srat_table()`.

### Control Flow
`get_rsdp_addr()` checks an existing `boot_params_ptr->acpi_rsdp_addr`, then EFI configuration tables, then BIOS EBDA and high-memory scan windows. EFI lookup prefers ACPI 2.0 GUID and falls back to ACPI 1.0 GUID. BIOS scanning validates both signature and checksums. `count_immovable_mem_regions()` ignores ACPI when `acpi=off`, finds SRAT via RSDP/XSDT/RSDT, walks subtables, and records non-hotpluggable memory affinity entries into `immovable_mem`.

### State, Persistence, And Dependencies
Persistent early state is `boot_params_ptr->acpi_rsdp_addr` set by `misc.c` and the global `immovable_mem` array used by KASLR. Dependencies include compressed EFI helpers, ACPI table definitions, command-line parsing, `boot_params`, and direct physical memory mapping.

### Integration Points
`extract_kernel()` saves the RSDP for the real kernel. `kaslr.c` calls `count_immovable_mem_regions()` to constrain placement when memory hotremove support wants the kernel in immovable memory.

### Risks
This code dereferences firmware-provided physical addresses before full kernel validation, so bad tables can cause early boot faults. SRAT parsing must reject zero-length subtables and cap the array at `MAX_NUMNODES*2`. Command-line `acpi_rsdp` is considered only for kexec-related builds and intentionally is not written back to boot params.

### Test Signals
Boot with EFI ACPI 2.0, EFI ACPI 1.0, BIOS RSDP, no ACPI, `acpi=off`, `acpi=rsdt`, kexec `acpi_rsdp=`, malformed checksums, zero-length SRAT entries, and many memory affinity entries.
