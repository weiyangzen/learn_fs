
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/fdt.c

Purpose: builds or updates the Flattened Device Tree used by EFI stub boots, injects EFI handoff data into `/chosen`, handles optional command-line DTB loading, records KASLR seed, updates final memory-map properties during ExitBootServices, installs the runtime virtual map, and enters the kernel.

Important APIs/types/functions: exports `efi_boot_kernel()` and `get_fdt()`. Important internals are `update_fdt()`, `update_fdt_memmap()`, `exit_boot_func()`, and `allocate_new_fdt_and_exit_boot()`.

Control flow: the file validates an existing DTB from command line or EFI config table, or creates an empty tree. It removes reserve-map entries, ensures `/chosen`, adds bootargs, EFI system table, memory-map placeholder properties, descriptor size/version placeholders, and optional `kaslr-seed`. It allocates a fixed-size new FDT, updates it, calls `efi_exit_boot_services()` with a callback that fills runtime-map entries and rewrites memory-map properties in place, then calls SetVirtualAddressMap unless disabled. `efi_boot_kernel()` optionally handles post-EBS ARM state and calls `efi_enter_kernel()`.

State and persistence behavior: the new FDT page allocation persists into the kernel boot path. Runtime-map pool memory is transient until SetVirtualAddressMap. EFI memory-map pointers are embedded into the FDT for early kernel parsing. Command-line DTBs are rejected under secure boot unless explicitly allowed and secure boot is disabled.

Dependencies and integration points: depends on libfdt, EFI memory-map helpers, random bytes, secure boot detection, command-line file loading, arch `efi_enter_kernel()`, and EFI runtime SetVirtualAddressMap. It integrates the EFI firmware world with Linux device-tree boot protocols.

Risks and test signals: risks include FDT size exhaustion, malformed/truncated firmware DTBs, unauthenticated `dtb=` under secure boot, allocations between GetMemoryMap and ExitBootServices, SetVirtualAddressMap failure after point-of-no-return, and wrong descriptor sizes. Test signals include boots with config-table DTB, command-line DTB, no DTB, secure boot enabled, FDT growth near `MAX_FDT_SIZE`, KASLR seed property presence, and final `/chosen/linux,uefi-*` values.
