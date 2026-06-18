
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch.c

Purpose: provides LoongArch EFI boot handoff logic after common stub setup, including cache sync, runtime virtual map setup, Direct Mapping Window configuration, and final kernel entry call.

Important APIs/types/functions: exports `check_platform_features()`, `efi_cache_sync_image()`, weak `kernel_entry_address()`, and `efi_boot_kernel()`. Internal `exit_boot_func()` populates runtime descriptors through `efi_get_virtmap()`.

Control flow: `efi_boot_kernel()` allocates a runtime virtmap, forces `efi_novamap` false, exits boot services with a callback that records runtime descriptors, calls SetVirtualAddressMap, programs LoongArch DMW CSR windows, computes the real kernel entry address, and calls it with EFI flag, command-line pointer, and system table pointer.

State and persistence behavior: writes architecture CSR state for direct mappings and passes EFI system table into the kernel. Runtime map pool allocation is used for SetVirtualAddressMap and not persisted separately.

Dependencies and integration points: depends on common EFI memory-map and boot-service helpers, LoongArch CSR/address-space definitions, and LoongArch kernel entry ABI.

Risks and test signals: SetVirtualAddressMap status is not checked, so firmware failures may surface later through runtime services. CSR DMW setup must match kernel expectations. Test signals include LoongArch EFI boot, zboot fallback entry calculation, runtime service availability, and cache coherency after relocation.
