
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.c

Purpose: implements the x86 EFI boot stub entry path, including boot_params allocation, command-line parsing, kernel decompression and placement, initrd handling, secure boot/RNG/TPM/GOP/PCI/Apple quirks, unaccepted memory setup, e820 construction, ExitBootServices, SEV setup, optional 5-level paging switch, and final jump.

Important APIs/types/functions: defines `efi_pe_entry()`, optional handover entries, `efi_stub_entry()`, `efi_adjust_memory_range_protection()`, and many x86 helpers such as `setup_e820()`, `exit_boot()`, `efi_decompress_kernel()`, `setup_efi_pci()`, `retrieve_apple_device_properties()`, and `setup_unaccepted_memory()`.

Control flow: entry validates the EFI system table, allocates boot params if not handed over, rejects unsupported SNP features, locates DXE services and Memory Attribute Protocol, prepares 5-level paging trampoline, parses built-in and loader command lines, propagates memory encryption flags, decompresses the kernel into randomized or bounded memory, loads initrd and updates boot params, records secure boot, reset mitigation, RNG seed, TPM log, graphics, PCI ROM setup data, Apple quirks, and unaccepted memory policy. It then exits boot services, fills EFI info and e820/e820ext from the final memory map, enables SEV while firmware exception state is still active, toggles 5-level paging if needed, and jumps to the decompressed kernel with boot params in RSI/ESI.

State and persistence behavior: global `efi_system_table`, `efi_dxe_table`, `image`, `memattr`, `cmdline_memmap_override`, boot params, setup_data chains, initrd table, e820 entries, unaccepted memory bitmap, and copied PCI/Apple data persist into kernel entry. Hardware/firmware state changes include memory attributes, boot-services exit, SEV enable, PCI bus-master changes, and possible paging mode toggle.

Dependencies and integration points: depends on x86 decompressor symbols/functions, EFI boot/file/GOP/PCI/Apple/DXE/Memory Attribute protocols, e820 types, SEV/SNP helpers, KASLR RNG, common initrd/random/TPM/secureboot helpers, and x86 boot ABI.

Risks and test signals: high-risk areas include decompression placement under `mem=`/`memmap=`/`hugepages=`, firmware memory protection quirks, Apple-specific protocol handling, e820 extension sizing, unaccepted memory table creation, ExitBootServices retry, SEV/SNP feature compatibility, and mixed handover/PE paths. Test signals include x86_32/x86_64/mixed-mode builds, handover protocol, KASLR on/off and AMI v2 quirk, external initrd override, secure boot, TPM event log, GOP/EDID, PCI option ROM preservation, e820ext overflow, SEV-SNP guests, and LA57 transitions.
