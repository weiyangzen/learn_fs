## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.c

### Purpose
`compressed/efi.c` provides minimal early helpers for reading EFI system and configuration tables from `boot_params` without including full kernel EFI headers.

### Important APIs, Types, And Functions
Exports are `efi_get_type()`, `efi_get_system_table()`, `efi_get_conf_table()`, and `efi_find_vendor_table()`. Internal helpers include `get_kexec_setup_data()` and `get_vendor_table()`.

### Control Flow
`efi_get_type()` validates the loader signature as `EL64` or `EL32` and rejects inaccessible high addresses on non-64-bit builds. `efi_get_system_table()` reconstructs the system-table physical address. `efi_get_conf_table()` handles 64-bit, 32-bit, and kexec-provided configuration tables. `efi_find_vendor_table()` walks entries and returns the vendor table address for a matching GUID.

### State, Persistence, And Dependencies
The file is stateless and reads `boot_params->efi_info` plus optional `SETUP_EFI` setup_data. Dependencies are local EFI structure definitions in `efi.h`, `boot_params`, setup_data traversal, and direct physical mappings of EFI tables.

### Integration Points
ACPI RSDP discovery, unaccepted-memory table discovery, EFI soft reserve handling, and other compressed boot firmware consumers use these helpers.

### Risks
Firmware-provided table lengths and addresses are trusted enough to walk in early boot. x86_32 cannot access EFI structures above 4 GiB. kexec handling intentionally falls back to normal EFI paths when setup_data is missing or incomplete, so callers must handle zero results.

### Test Signals
Boot EFI32, EFI64, no-EFI, mixed high-address x86_32 failure, kexec with `SETUP_EFI`, and vendor table lookup for ACPI and unaccepted-memory GUIDs.
