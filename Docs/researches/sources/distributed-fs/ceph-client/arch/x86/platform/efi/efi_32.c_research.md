<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c

## Purpose
`efi_32.c` provides 32-bit x86 EFI runtime mapping and calling support. It maps EFI runtime descriptors into the kernel's existing address space or cached I/O mappings, performs the physical-mode `SetVirtualAddressMap()` call through an assembly stub, and marks runtime code executable when NX is supported.

## Important APIs, types, and functions
Important functions are `efi_map_region()`, `efi_alloc_page_tables()`, `efi_sync_low_kernel_mappings()`, `efi_dump_pagetable()`, `efi_setup_page_tables()`, `efi_map_region_fixed()`, `parse_efi_setup()`, `efi_set_virtual_address_map()`, `efi_runtime_update_mappings()`, `arch_efi_call_virt_setup()`, and `arch_efi_call_virt_teardown()`. The assembly entry `efi_call_svam()` is declared here.

## Control flow
For each runtime descriptor, `efi_map_region()` uses the direct kernel mapping if the PFN range is already mapped, setting UC attributes for non-WB memory, or `ioremap_cache()` otherwise. `efi_set_virtual_address_map()` switches CR3 to `initial_page_table`, loads a physical GDT, disables interrupts, calls the physical-mode stub, then restores the fixmap GDT, original page tables, and TLB state. Runtime call setup only brackets FPU and firmware branch-speculation restrictions.

## State and persistence behavior
The file stores no private persistent state. It writes `md->virt_addr` in EFI descriptors and may alter page attributes for runtime regions. Several functions are no-ops because 32-bit does not use a separate `efi_mm`.

## Dependencies and integration points
It depends on x86 GDT/CR3/TLB manipulation, `efi_stub_32.S`, memory attribute APIs, EFI generic virtual-mode orchestration in `efi.c`, and FPU/speculation firmware wrappers.

## Risks and edge cases
The `SetVirtualAddressMap()` path temporarily disables paging in the stub and relies on low physical mappings and a valid GDT. Non-WB mappings must be made uncached. Null ioremap results are logged but still leave runtime services vulnerable unless higher-level code disables them.

## Test signals
32-bit EFI boot with runtime variables, non-WB runtime descriptors, NX-enabled kernels, EFI page-table dumps, and `SetVirtualAddressMap()` failures are important validation cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_32.c -->
