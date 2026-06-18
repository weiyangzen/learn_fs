
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub.c

Purpose: implements the shared ARM/ARM64/RISC-V-style EFI stub common path: command-line handling, primary display capture, event log retrieval, reset-attack mitigation, initrd and RNG seed setup, EFI memreserve table installation, runtime virtual-map construction, and handoff to `efi_boot_kernel()`.

Important APIs/types/functions: exports `efi_handle_cmdline()`, `efi_stub_common()`, `efi_alloc_virtmap()`, and `efi_get_virtmap()`. Internal helpers allocate a primary display table, install `LINUX_EFI_MEMRESERVE_TABLE_GUID`, and read `EFI_RT_PROPERTIES_TABLE_GUID`.

Control flow: `efi_handle_cmdline()` converts firmware load options, parses EFI options unless forced, parses built-in command lines when configured, and returns pool-owned command-line memory. `efi_stub_common()` runs platform feature checks, captures GOP/sysfb data, retrieves TPM logs, enables memory overwrite request mitigation, loads initrd, installs RNG seed and memreserve tables, forces `efi_novamap` if runtime SetVirtualAddressMap is unsupported, then calls the architecture's `efi_boot_kernel()`. Runtime virtual map generation scans EFI memory descriptors, sets `virt_addr` for runtime regions, and either creates a compact low virtual map or records flat offsets/physical mappings when requested.

State and persistence behavior: `virtmap_base` and `flat_va_mapping` guide runtime virtual address assignment. The memreserve table and primary display data are installed in EFI configuration tables for the kernel. No disk persistence exists; all data is boot-time firmware/kernel handoff state.

Dependencies and integration points: depends on GOP setup, TPM/random/initrd helpers, EFI runtime properties, architecture `check_platform_features()`, `efi_boot_kernel()`, `efi_enter_kernel()`, and optional `free_primary_display()` overrides. It is the central common wrapper used by non-x86 EFI stubs and zboot after decompression.

Risks and test signals: important risks are incomplete runtime-service support reporting, conflicts in virtual address assignment, failure to free primary display data after failed boot, and missing command-line parsing when `CONFIG_CMDLINE_FORCE` changes behavior. Test signals include booting with and without SetVirtualAddressMap support, kexec between different page sizes, GOP/EDID capture, memreserve table presence, initrd and RNG configuration tables, and error paths from platform feature checks.
