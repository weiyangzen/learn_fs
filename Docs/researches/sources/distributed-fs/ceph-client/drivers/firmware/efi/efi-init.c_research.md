# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-init.c

Purpose: initializes EFI on FDT-based architectures by reading EFI boot parameters from the device tree, mapping the EFI memory map and system table, parsing config tables, populating memblock from EFI memory descriptors, and setting up display/table side effects.

Important APIs/types/functions: exports/defines `primary_display_table`, `sysfb_primary_display` on non-x86, and `efi_init()`. Helpers include `is_memory()`, `efi_to_phys()`, `init_primary_display()`, `uefi_init()`, `is_usable_memory()`, and `reserve_regions()`.

Control flow: `efi_init()` obtains system-table and memmap parameters via `efi_get_fdt_params()`, initializes the early EFI memmap, validates descriptor version, maps and checks the system table, records runtime pointer/version, reports firmware header, parses config tables, and then rebuilds memblock from EFI memory descriptors. Usable writeback memory is added as RAM; non-usable memory is nomapped; ACPI reclaim memory is reserved; special-purpose memory can be skipped for soft reservation. It then caps usable ranges, finds mirrored memory, initializes ESRT and MOK variable tables, reserves the memmap, and initializes primary display data when relevant.

State and persistence behavior: sets `efi.flags`, `efi.runtime`, config table globals, memblock memory/reservation state, primary display state, and reserved EFI memmap storage.

Dependencies and integration points: depends on FDT parameters, EFI memmap/config parser, memblock, OF memory helpers, KHO scratch preservation, sysfb/earlycon, ESRT, MOK variables, and architecture EFI support.

Risks and test signals: if the EFI memory map cannot be mapped, boot panics because no other reliable memory description exists. Incorrect memblock rebuilding can hide RAM or expose reserved regions. Test signals include EFI boot logs, correct `/proc/iomem` RAM/reserved layout, sysfb early console reprobe, ESRT availability, and successful FDT EFI boot on ARM/RISC-V-like platforms.
