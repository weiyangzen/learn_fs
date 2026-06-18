
# sources/distributed-fs/ceph-client/drivers/firmware/efi/memmap.c

Purpose: maps, unmaps, and remaps the kernel's persistent EFI memory map representation during early and late boot.

Important APIs/types/functions: exports `__efi_memmap_init()`, `efi_memmap_init_early()`, `efi_memmap_unmap()`, and `efi_memmap_init_late()`.

Control flow: common init chooses `early_memremap()` or `memremap()` based on `EFI_MEMMAP_LATE`, fills `efi.memmap` fields, computes entry count and end pointer, and sets the `EFI_MEMMAP` flag. Early init clears flags and maps via early remap. Unmap chooses early or late unmap and clears state. Late init asserts early mapping was removed, copies descriptor metadata from the prior map, and remaps the physical map with `memremap()`.

State and persistence behavior: global `efi.memmap` and `efi.flags` are updated. The late mapping persists for runtime services and EFI descriptor lookups.

Dependencies and integration points: depends on early ioremap, memremap, EFI global state, and runtime setup code such as RISC-V's `riscv_enable_runtime_services()`.

Risks and test signals: forgetting to unmap early fixmap space, descriptor metadata mismatch, and failed remap leave EFI runtime support degraded. Test signals include early map success, unmap idempotence, late remap after vmalloc setup, EFI_MEMMAP flag transitions, and `efi_mem_desc_lookup()` after late mapping.
