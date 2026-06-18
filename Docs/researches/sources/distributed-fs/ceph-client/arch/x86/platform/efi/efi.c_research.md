<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c

## Purpose
`efi.c` is the common x86 EFI bring-up and runtime virtual-mode coordinator. It imports firmware tables, initializes and sanitizes the EFI memory map, optionally folds EFI memory into E820, removes problematic MMIO reservations, maps runtime regions, calls `SetVirtualAddressMap()`, installs native or mixed runtime services, and exposes EFI table addresses through sysfs attributes.

## Important APIs, types, and functions
Key functions are `efi_memblock_x86_reserve_range()`, `efi_init()`, `efi_clean_memmap()`, `efi_remove_e820_mmio()`, `efi_print_memmap()`, `efi_systab_init()`, `efi_config_init()`, `efi_merge_regions()`, `efi_map_regions()`, `kexec_enter_virtual_mode()`, `__efi_enter_virtual_mode()`, `efi_enter_virtual_mode()`, `efi_is_table_address()`, `efi_attr_is_visible()`, and `__x86_efi_boot_mode()`. State includes `efi_systab_phys`, `efi_runtime`, `efi_nr_tables`, `efi_fw_vendor`, `efi_config_table`, and `efi_setup`.

## Control flow
Early memory reservation maps the bootloader-provided EFI memory map, optionally imports it into E820, reserves the map storage, and marks boot-services preservation. `efi_init()` maps and validates the system table, parses config tables, checks runtime support/disable options, sanitizes bad descriptors, removes large EFI MMIO ranges from E820, and marks runtime services available. `efi_enter_virtual_mode()` later either reuses kexec mappings or builds new EFI page tables, maps required regions, installs a late memory map, calls `efi_set_virtual_address_map()`, checks embedded firmware, unmaps boot services, installs runtime call handlers, updates permissions, and deletes the dummy variable used by quirks.

## State and persistence behavior
EFI table physical addresses are retained for sysfs and table-address checks. The EFI memory map transitions from early mapping to late mapping. Runtime service availability is represented by bits in `efi.flags`. New runtime memory maps contain only mapped descriptors with assigned virtual addresses.

## Dependencies and integration points
It depends on boot parameters, EFI generic table parsing, memblock, E820, early memremap, kexec setup_data, architecture-specific mapping functions in `efi_32.c`/`efi_64.c`, EFI quirks, BGRT/ESRT/TPM/RNG/MOK/CoCo tables, sysfs EFI attributes, and runtime service setup.

## Risks and edge cases
32-bit kernels cannot handle EFI tables or maps above 4GB. Invalid descriptor overflow must be removed before use. Firmware may require boot-services mappings even after ExitBootServices. Mixed-mode and kexec paths have different mapping constraints. Removing large EFI MMIO from E820 helps PCI hotplug but must preserve small non-window MMIO.

## Test signals
EFI boots across 32/64-bit, mixed mode, kexec, `add_efi_memmap`, `efi=noruntime`, `efi=debug`, soft-reserve memory, large MMIO host windows, and malformed memory maps. Validate runtime variables, sysfs table attributes, E820 output, and `SetVirtualAddressMap()` status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi.c -->
