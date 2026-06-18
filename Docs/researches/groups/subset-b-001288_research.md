# subset-b-001288 research

This grouped report covers the EFI boot stub helpers, architecture-specific EFI entry paths, EFI runtime service wrappers, and EFI firmware table exposure files in the assigned Ceph-client source mirror. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-helper.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-helper.c

Purpose: provides shared EFI stub helper code for command-line option parsing, firmware load-option quirks, measured boot events, command-line conversion, ExitBootServices retry handling, EFI configuration table lookup, initrd loading, key wait, and post-decompression image permission remapping.

Important APIs/types/functions: exports `efi_parse_options()`, `efi_apply_loadoptions_quirk()`, `efi_convert_cmdline()`, `efi_exit_boot_services()`, `get_efi_config_table()`, `efi_load_initrd()`, `efi_wait_for_key()`, and `efi_remap_image()`. Important internal types include EFI load-option unpacking structures and TCG2/CC tagged event wrappers used by `efi_measure_tagged_event()`.

Control flow: command-line parsing copies EFI load options into pool memory, tokenizes args, and updates global stub flags such as `efi_nokaslr`, `efi_nochunk`, `efi_novamap`, `efi_noinitrd`, `efi_no5lvl`, `efi_mem_encrypt`, and PCI-DMA-disabling behavior. `efi_convert_cmdline()` measures raw LoadOptions, applies Dell descriptor quirks, counts UTF-8 output safely, truncates at a whitespace boundary when possible, and formats UTF-16 options into an ASCII/UTF-8 command line. `efi_exit_boot_services()` obtains the memory map, lets the caller mutate it, calls ExitBootServices, and performs the UEFI-specified single retry with the same buffer on `EFI_INVALID_PARAMETER`. Initrd loading first tries the Linux LoadFile2 device path, falls back to `initrd=` files, measures successful payloads, and installs the Linux initrd configuration table. `efi_remap_image()` optionally uses EFI Memory Attribute Protocol to set code RO/executable and data NX.

State and persistence behavior: most state is global boot-stub process state (`efi_nochunk`, `efi_nokaslr`, `efi_novamap`, `efi_mem_encrypt`, soft-reserve and PCI-DMA flags). Pool/page allocations for command lines, initrds, event records, and config tables survive only through boot unless installed as EFI configuration tables. The random/measurement/config-table outputs are handed to the kernel through EFI tables rather than files.

Dependencies and integration points: depends on EFI boot services, runtime variable access macros, TCG2 and Confidential Computing measurement protocols, LoadFile2, EFI Memory Attribute Protocol, `handle_cmdline_files()`, `efi_pci_disable_bridge_busmaster()`, and architecture code that supplies initrd limits and image-remap needs. It is used by common ARM/RISC-V/LoongArch zboot and x86 paths.

Risks and test signals: risk centers on firmware quirks: malformed load options, truncated UTF-16/surrogate handling, memory-map changes between map retrieval and ExitBootServices, LoadFile2 size mismatches, initrd measurement failures, and firmware memory-attribute bugs. Test signals include `efi=` option combinations, Dell Boot#### load-option descriptors, long command lines, multiple initrd sources, PCR9 measurement logs, ExitBootServices retry coverage, PCI bus-master disable paths, and image W^X attribute changes on firmware with and without Memory Attribute Protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub.c

Purpose: implements the shared ARM/ARM64/RISC-V-style EFI stub common path: command-line handling, primary display capture, event log retrieval, reset-attack mitigation, initrd and RNG seed setup, EFI memreserve table installation, runtime virtual-map construction, and handoff to `efi_boot_kernel()`.

Important APIs/types/functions: exports `efi_handle_cmdline()`, `efi_stub_common()`, `efi_alloc_virtmap()`, and `efi_get_virtmap()`. Internal helpers allocate a primary display table, install `LINUX_EFI_MEMRESERVE_TABLE_GUID`, and read `EFI_RT_PROPERTIES_TABLE_GUID`.

Control flow: `efi_handle_cmdline()` converts firmware load options, parses EFI options unless forced, parses built-in command lines when configured, and returns pool-owned command-line memory. `efi_stub_common()` runs platform feature checks, captures GOP/sysfb data, retrieves TPM logs, enables memory overwrite request mitigation, loads initrd, installs RNG seed and memreserve tables, forces `efi_novamap` if runtime SetVirtualAddressMap is unsupported, then calls the architecture's `efi_boot_kernel()`. Runtime virtual map generation scans EFI memory descriptors, sets `virt_addr` for runtime regions, and either creates a compact low virtual map or records flat offsets/physical mappings when requested.

State and persistence behavior: `virtmap_base` and `flat_va_mapping` guide runtime virtual address assignment. The memreserve table and primary display data are installed in EFI configuration tables for the kernel. No disk persistence exists; all data is boot-time firmware/kernel handoff state.

Dependencies and integration points: depends on GOP setup, TPM/random/initrd helpers, EFI runtime properties, architecture `check_platform_features()`, `efi_boot_kernel()`, `efi_enter_kernel()`, and optional `free_primary_display()` overrides. It is the central common wrapper used by non-x86 EFI stubs and zboot after decompression.

Risks and test signals: important risks are incomplete runtime-service support reporting, conflicts in virtual address assignment, failure to free primary display data after failed boot, and missing command-line parsing when `CONFIG_CMDLINE_FORCE` changes behavior. Test signals include booting with and without SetVirtualAddressMap support, kexec between different page sizes, GOP/EDID capture, memreserve table presence, initrd and RNG configuration tables, and error paths from platform feature checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efistub.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efistub.h

Purpose: private EFI stub ABI header defining mixed-mode-safe protocol unions, boot/runtime service call wrappers, EFI protocol structures, helper macros, global flags, and cross-file prototypes for stub memory, graphics, FDT, initrd, random, secure boot, SMBIOS, KASLR, unaccepted memory, and zboot code.

Important APIs/types/functions: key macros are `efi_table_attr()`, `efi_fn_call()`, `efi_call_proto()`, `efi_bs_call()`, `efi_rt_call()`, `efi_dxe_call()`, logging wrappers, FDT property setters, EFI variable wrappers, and mixed-mode handle/event helpers. It defines EFI boot services, DXE services, memory attribute protocol, text/graphics/file/PCI/Apple/TCG2/CC/SMBIOS/RISC-V boot/LoadFile protocol layouts plus prototypes for all major helper files.

Control flow: the header has no executable top-level flow, but it defines how all stub C files call firmware through native or mixed-mode tables, how output logging is gated, how config-table and file-protocol data is represented, and which functions each architecture must supply.

State and persistence behavior: declares global boot-stub flags and global EFI system/DXE table pointers. Structures mirror firmware tables or configuration-table payloads and are live only during boot or passed to the kernel by pointer.

Dependencies and integration points: depends on Linux EFI definitions, compiler cleanup helpers, architecture EFI wrappers, FDT APIs, sysfb, and arch-specific image alignment/cache/entry functions. It is the integration hub among libstub files and between common code and x86/RISC-V/LoongArch/ARM-specific implementations.

Risks and test signals: ABI risk is high because field order and pointer width in protocol unions must match UEFI native and mixed-mode layouts. Prototype drift breaks cross-arch builds. Test signals are all EFI-stub build matrices, mixed-mode x86 boot, GOP/file/PCI protocol calls, TCG2/CC measurement calls, and compile-time coverage for optional config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efistub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/fdt.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/fdt.c

Purpose: builds or updates the Flattened Device Tree used by EFI stub boots, injects EFI handoff data into `/chosen`, handles optional command-line DTB loading, records KASLR seed, updates final memory-map properties during ExitBootServices, installs the runtime virtual map, and enters the kernel.

Important APIs/types/functions: exports `efi_boot_kernel()` and `get_fdt()`. Important internals are `update_fdt()`, `update_fdt_memmap()`, `exit_boot_func()`, and `allocate_new_fdt_and_exit_boot()`.

Control flow: the file validates an existing DTB from command line or EFI config table, or creates an empty tree. It removes reserve-map entries, ensures `/chosen`, adds bootargs, EFI system table, memory-map placeholder properties, descriptor size/version placeholders, and optional `kaslr-seed`. It allocates a fixed-size new FDT, updates it, calls `efi_exit_boot_services()` with a callback that fills runtime-map entries and rewrites memory-map properties in place, then calls SetVirtualAddressMap unless disabled. `efi_boot_kernel()` optionally handles post-EBS ARM state and calls `efi_enter_kernel()`.

State and persistence behavior: the new FDT page allocation persists into the kernel boot path. Runtime-map pool memory is transient until SetVirtualAddressMap. EFI memory-map pointers are embedded into the FDT for early kernel parsing. Command-line DTBs are rejected under secure boot unless explicitly allowed and secure boot is disabled.

Dependencies and integration points: depends on libfdt, EFI memory-map helpers, random bytes, secure boot detection, command-line file loading, arch `efi_enter_kernel()`, and EFI runtime SetVirtualAddressMap. It integrates the EFI firmware world with Linux device-tree boot protocols.

Risks and test signals: risks include FDT size exhaustion, malformed/truncated firmware DTBs, unauthenticated `dtb=` under secure boot, allocations between GetMemoryMap and ExitBootServices, SetVirtualAddressMap failure after point-of-no-return, and wrong descriptor sizes. Test signals include boots with config-table DTB, command-line DTB, no DTB, secure boot enabled, FDT growth near `MAX_FDT_SIZE`, KASLR seed property presence, and final `/chosen/linux,uefi-*` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/file.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/file.c

Purpose: implements EFI-stub file loading from `initrd=` and `dtb=` style command-line options, including same-volume lookup, optional text device-path lookup, concatenation of multiple files, chunked reads, and allocation under soft/hard limits.

Important APIs/types/functions: exports `handle_cmdline_files()`. Internals include `efi_open_file()`, `efi_open_volume()`, `find_file_option()`, and `efi_open_device_path()`. `struct finfo` combines `efi_file_info_t` with a bounded UTF-16 filename buffer.

Control flow: the loader applies load-option quirks, chooses firmware or built-in command lines depending on config, scans for the requested option prefix, resolves either an explicit EFI text device path or the kernel image volume, opens the file, obtains its size, grows a single EFI page allocation when concatenating files, reads data in 1 MiB chunks on x86 unless `efi=nochunk`, closes handles, and repeats for multiple occurrences and optional built-in second pass.

State and persistence behavior: the loaded files are returned as one contiguous EFI page allocation with address/size stored through caller pointers. Open file and volume protocol handles are transient. No durable state exists.

Dependencies and integration points: depends on EFI Simple File System, File Protocol, Device Path From Text Protocol, `efi_allocate_pages()`, `efi_free()`, load-option quirks, and config-command-line policy. It is used by initrd and DTB loading helpers.

Risks and test signals: filename parsing is bounded to 256 UTF-16 code units and stops on space/newline/NUL, so paths with spaces are unsupported. Chunked reads fix some firmware but break others, hence the `nochunk` option. Reallocation while concatenating must preserve prior file content and free old pages. Test signals include multiple initrd files, absolute EFI device paths, same-volume paths with `/` conversion to `\`, forced/extended built-in command lines, allocation failure unwinds, and corrupt read/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/find.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/find.c

Purpose: supplies minimal bitmap search helpers for the EFI stub environment where the full kernel library may not be available.

Important APIs/types/functions: exports `_find_next_bit()` and `_find_next_zero_bit()`, both implemented through the local `FIND_NEXT_BIT` macro using word masks, `__ffs()`, and `BITMAP_FIRST_WORD_MASK()`.

Control flow: the macro validates the start bit, masks the first word, scans subsequent bitmap words until a nonzero candidate is found or the size is exhausted, and returns either the found bit index or `nbits`.

State and persistence behavior: no state. The functions only inspect caller-provided bitmap memory.

Dependencies and integration points: depends on Linux bitmap/bitops helpers and is used by stub code such as unaccepted-memory bitmap iteration when linked without full lib support.

Risks and test signals: callers must provide enough bitmap words for `nbits`; the helper assumes native-endian unsigned long bitmaps. Test signals are boundary searches at zero, at the final bit, beyond `nbits`, all-set/all-clear maps, and maps spanning multiple words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/gop.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/gop.c

Purpose: parses `video=efifb:` graphics options, selects an EFI Graphics Output Protocol mode, populates Linux `screen_info`, and copies EDID data for the primary display.

Important APIs/types/functions: exports `efi_parse_option_graphics()` and `efi_setup_graphics()`. Internal mode selectors include `choose_mode_modenum()`, `choose_mode_res()`, `choose_mode_auto()`, `choose_mode_list()`, `set_mode()`, `setup_screen_info()`, `setup_edid_info()`, and `find_handle_with_primary_gop()`.

Control flow: option parsing recognizes `mode=N`, `WxH[-depth|rgb|bgr]`, `auto`, and `list`. Setup locates all GOP handles, chooses a GOP that also supports ConOut when possible, applies requested mode changes, fills framebuffer base, resolution, stride, depth, pixel bit positions, 64-bit base capability, and skip-quirks flag, then reads active or discovered EDID protocol data.

State and persistence behavior: static `cmdline` stores the requested graphics policy until setup. Resulting framebuffer/EDID state is persisted into `screen_info`/`edid_info` or a primary display config table consumed by the kernel.

Dependencies and integration points: depends on EFI GOP, EDID protocols, console input for `list`, EFI printing/key wait, and Linux `screen_info`/sysfb consumers. It is called by common and x86 EFI stubs.

Risks and test signals: firmware may expose splitter GOP handles, BLT-only modes, invalid pixel formats, or missing EDID. `auto` chooses maximum area and depth, which may select modes firmware cannot set reliably. Test signals include explicit mode numbers, resolution/depth matching, list timeout/key path, primary ConOut selection, 64-bit framebuffer bases, bitmask pixel formats, and EDID active/discovered fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/gop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/intrinsics.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/intrinsics.c

Purpose: provides minimal memory intrinsics for the EFI stub, using firmware copy/set services before ExitBootServices and local byte loops afterward or when boot services are unavailable.

Important APIs/types/functions: exports `memcpy()`, `memmove()` as an alias, `memset()`, and `memcmp()`. Under KASAN it aliases compiler-emitted `__memcpy`, `__memmove`, and `__memset`.

Control flow: `memcpy()` checks whether boot services are available; before EBS it delegates to `boottime->copy_mem`, otherwise it uses overlap-safe `efistub_memmove()`. `memset()` similarly delegates to `boottime->set_mem` or a local loop. `memcmp()` compares byte-by-byte.

State and persistence behavior: no independent state. Behavior depends on the current validity of `efi_system_table->boottime`.

Dependencies and integration points: depends on EFI system table access and arch string declarations. It backs many stub files that cannot rely on full kernel libc.

Risks and test signals: `memcpy()` is overlap-safe because it uses memmove semantics locally, but firmware `copy_mem` semantics must also be valid for its callers. Test signals include pre/post-EBS copy and memset, overlapping ranges, KASAN builds, and compiler intrinsic emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/intrinsics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/kaslr.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/kaslr.c

Purpose: obtains EFI RNG seed material for physical KASLR and relocates kernel images to either randomized or safe aligned physical memory.

Important APIs/types/functions: exports `efi_kaslr_get_phys_seed()` and `efi_kaslr_relocate_kernel()`. Internal `check_image_region()` detects loader-provided images whose BSS crosses EFI memory descriptors.

Control flow: seed acquisition checks `CONFIG_RANDOMIZE_BASE`, `efi_nokaslr`, and the fixed-placement protocol, then uses `efi_get_random_bytes()` or disables KASLR on failure. Relocation first attempts `efi_random_alloc()` when seeded. On failure it may execute in place if placement/alignment/BSS coverage are acceptable, otherwise allocates aligned pages, copies image bytes, updates `image_addr`, syncs instruction cache, and remaps code/data permissions.

State and persistence behavior: modifies caller-owned image/reserve addresses and global `efi_nokaslr` on RNG failure. Relocated pages persist into kernel entry; original allocations are handled by architecture code.

Dependencies and integration points: depends on EFI RNG, memory map helpers, `efi_random_alloc()`, `efi_allocate_pages_aligned()`, arch image alignment, cache sync, and `efi_remap_image()`. Used by RISC-V and similar non-x86 stubs.

Risks and test signals: risk includes weak/no RNG, fixed loader placement, GRUB BSS allocation bugs, incorrect minimum alignment, and copy/remap failures. Test signals include KASLR enabled/disabled command lines, fixed placement protocol, RNG unavailable, image already aligned in place, BSS overlap diagnostics, and successful randomized relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.c

Purpose: implements LoongArch EFI stub kernel relocation from firmware-loaded image memory to an architecture-acceptable aligned physical location.

Important APIs/types/functions: exports `handle_kernel_image()` and `kernel_entry_address()`. Internal `efi_relocate_kernel()` allocates at `EFI_KIMG_PREFERRED_ADDRESS` or lowest suitable memory and copies the kernel file image.

Control flow: `handle_kernel_image()` derives the firmware image base, relocates `kernel_fsize` bytes into an allocation of `kernel_asize`, updates `image_addr` and `image_size`, and returns status. `kernel_entry_address()` converts the linked `kernel_entry` symbol offset from the original image base to the relocated base.

State and persistence behavior: uses linker-provided `kernel_asize`, `kernel_fsize`, and `kernel_entry` symbols. The relocated allocation persists into kernel entry; no global persistent state is added.

Dependencies and integration points: depends on LoongArch address/cache helpers, `efi_low_alloc_above()`, EFI page allocation, and the common stub `handle_kernel_image()` contract.

Risks and test signals: preferred-address allocation may fail, fallback must respect alignment, and image sizes must match linker/header data. Test signals include preferred-address success/failure, low allocation fallback, copied image checksum/entry offset, and cache sync before execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.h

Purpose: declares the LoongArch stub helper for deriving the relocated kernel entry address.

Important APIs/types/functions: declares `kernel_entry_address(unsigned long kernel_addr, efi_loaded_image_t *image)`.

Control flow: no executable flow. The declaration lets LoongArch common boot code call either the strong implementation from `loongarch-stub.c` or the weak fallback in `loongarch.c`.

State and persistence behavior: no state.

Dependencies and integration points: depends on `efi_loaded_image_t` from `efistub.h` being visible before inclusion. It connects LoongArch relocation and final boot handoff code.

Risks and test signals: prototype mismatch would break LoongArch EFI builds. Test signal is successful linked builds with both normal and zboot LoongArch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch.c

Purpose: provides LoongArch EFI boot handoff logic after common stub setup, including cache sync, runtime virtual map setup, Direct Mapping Window configuration, and final kernel entry call.

Important APIs/types/functions: exports `check_platform_features()`, `efi_cache_sync_image()`, weak `kernel_entry_address()`, and `efi_boot_kernel()`. Internal `exit_boot_func()` populates runtime descriptors through `efi_get_virtmap()`.

Control flow: `efi_boot_kernel()` allocates a runtime virtmap, forces `efi_novamap` false, exits boot services with a callback that records runtime descriptors, calls SetVirtualAddressMap, programs LoongArch DMW CSR windows, computes the real kernel entry address, and calls it with EFI flag, command-line pointer, and system table pointer.

State and persistence behavior: writes architecture CSR state for direct mappings and passes EFI system table into the kernel. Runtime map pool allocation is used for SetVirtualAddressMap and not persisted separately.

Dependencies and integration points: depends on common EFI memory-map and boot-service helpers, LoongArch CSR/address-space definitions, and LoongArch kernel entry ABI.

Risks and test signals: SetVirtualAddressMap status is not checked, so firmware failures may surface later through runtime services. CSR DMW setup must match kernel expectations. Test signals include LoongArch EFI boot, zboot fallback entry calculation, runtime service availability, and cache coherency after relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/mem.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/mem.c

Purpose: provides EFI stub memory-map retrieval and page allocation/free helpers with Linux-specific slack, alignment, soft-reserve, and low-address allocation policies.

Important APIs/types/functions: exports `efi_get_memory_map()`, `efi_allocate_pages()`, `efi_free()`, and `efi_low_alloc_above()`.

Control flow: memory-map retrieval first probes descriptor size, allocates a buffer with `EFI_MMAP_NR_SLACK_SLOTS`, optionally installs it as the Linux boot memmap configuration table before the final GetMemoryMap, and returns ownership to the caller. Page allocation honors `EFI_ALLOC_LIMIT`, `EFI_ALLOC_ALIGN`, and maximum-address allocation semantics. Low allocation scans conventional memory descriptors, skips hot-pluggable and soft-reserved memory, rounds to requested alignment, and allocates at exact addresses.

State and persistence behavior: allocations are EFI page or pool allocations owned by callers. Installing the boot memmap table makes the map visible to the kernel. No local static state exists.

Dependencies and integration points: depends on EFI boot services, Linux EFI memory descriptor helpers, soft-reserve policy, and aligned allocation fallback supplied elsewhere. It is used by almost every stub subsystem.

Risks and test signals: off-by-one maximum-address math, descriptor slack sufficiency, soft-reserve skipping, and freeing with the same alignment granularity are key risks. Test signals include memory-map installation, ExitBootServices retry using slack, low allocations above a minimum, high-limit allocations, hotplug/SP memory exclusion, and allocation/free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/pci.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/pci.c

Purpose: mitigates early boot DMA risk by disconnecting non-root, non-VGA PCI devices and disabling bus mastering on PCI bridges before ExitBootServices when requested.

Important APIs/types/functions: exports `efi_pci_disable_bridge_busmaster()`.

Control flow: the function locates all EFI PCI I/O protocol handles, first disconnects drivers for devices behind bus 0 except VGA display controllers, then rescans handles for PCI bridges and clears `PCI_COMMAND_MASTER` in their command registers.

State and persistence behavior: it changes firmware-managed PCI device/bridge state in hardware config space. No software state is retained.

Dependencies and integration points: depends on EFI PCI I/O Protocol, PCI config constants, `disconnect_controller`, and `efi=disable_early_pci_dma` option parsing from helper code.

Risks and test signals: disabling bridges may affect devices firmware still expects, while skipping VGA protects framebuffer but not every display transport. Test signals include systems with PCIe bridges and GOP framebuffer, command register changes, no regression when protocol enumeration fails, and boot with/without the early PCI DMA mitigation option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/primary_display.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/primary_display.c

Purpose: allocates and publishes EFI primary display information for sysfb consumers when direct access to the kernel global is unavailable, especially zboot.

Important APIs/types/functions: exports `__alloc_primary_display()` and `free_primary_display()`.

Control flow: allocation reserves an `EFI_ACPI_RECLAIM_MEMORY` pool object, zeroes it, installs it under `LINUX_EFI_PRIMARY_DISPLAY_TABLE_GUID`, and returns it. Freeing removes the configuration table and frees the pool allocation.

State and persistence behavior: the display-info object persists as an EFI configuration table until consumed by the kernel or explicitly freed after failed/common boot handoff.

Dependencies and integration points: depends on EFI boot services and Linux `sysfb_display_info`. It is called by common stub display setup and zboot's `alloc_primary_display()` wrapper.

Risks and test signals: failure to uninstall on error leaves stale table data. Test signals include zboot framebuffer earlycon availability, config-table presence/absence around allocation/free, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/primary_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/printk.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/printk.c

Purpose: implements EFI stub console logging with UTF-8 to UCS-2 conversion, loglevel filtering, kernel-style prefixes, and bounded formatting.

Important APIs/types/functions: exports `efi_char16_puts()`, `efi_puts()`, and `efi_printk()`. Internal `utf8_to_utf32()` decodes UTF-8 and validates surrogate/range rules.

Control flow: `efi_puts()` chunks UTF-8 text into a 128-character EFI CHAR16 buffer, inserts carriage returns before newlines, encodes non-BMP characters as surrogate pairs, and calls ConOut. `efi_printk()` reads the leading kernel loglevel, filters by global `efi_loglevel`, formats with the stub `vsnprintf()` into 256 bytes, prints an EFI stub prefix for numbered levels, and emits a truncation notice if needed.

State and persistence behavior: global `efi_loglevel` defaults to notice and is changed by `quiet` or `efi=debug`. No persistent state exists.

Dependencies and integration points: depends on EFI Simple Text Output Protocol, local `vsnprintf()`, kernel loglevel helpers, and command-line parsing. Used by all stub diagnostics.

Risks and test signals: output is truncated at 255 bytes, invalid UTF-8 falls back to byte output, and firmware consoles can be slow or missing. Test signals include quiet/debug options, multi-byte UTF-8 output, newline CRLF conversion, truncation path, and calls before/after console availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/random.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/random.c

Purpose: obtains entropy from EFI RNG and optional EFI variables, then installs a Linux random seed configuration table for kernel RNG initialization and kexec continuity.

Important APIs/types/functions: exports `efi_get_random_bytes()` and `efi_random_get_seed()`. Defines a local mixed-mode `efi_rng_protocol_t`.

Control flow: direct random bytes locate EFI RNG Protocol and call `get_rng`. Seed installation locates RNG, probes a `RandomSeed` EFI variable, merges a prior bootloader seed table if small, allocates ACPI reclaim memory, tries raw RNG then any RNG algorithm, reads and deletes the nonvolatile seed variable when present, appends prior seed data, installs `LINUX_EFI_RANDOM_SEED_TABLE_GUID`, and wipes/free old or failed seed buffers.

State and persistence behavior: installed seed table persists into the kernel and across kexec while the old table is zeroed/freed after replacement. The `RandomSeed` EFI variable is consumed and deleted. No local static state remains.

Dependencies and integration points: depends on EFI RNG Protocol, EFI variable runtime calls in boot context, config-table lookup/install, and `memzero_explicit()`. Called by common and x86 EFI paths.

Risks and test signals: entropy can be unavailable, raw algorithm unsupported, EFI variable deletion may not erase storage, and corrupted prior seed size is capped. Test signals include RNG present/absent, raw unsupported fallback, `RandomSeed` variable consumption, prior seed concatenation, installed table size, and buffer zeroing on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/randomalloc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/randomalloc.c

Purpose: chooses a randomized aligned EFI memory allocation slot from suitable conventional memory, preferring mirrored/more-reliable memory when available.

Important APIs/types/functions: exports `efi_random_alloc()`. Internal `get_entry_num_slots()` counts candidate aligned placements per EFI descriptor, with descriptor `virt_addr` reused as a temporary slot-count field via `MD_NUM_SLOTS()`.

Control flow: the function retrieves the memory map, normalizes alignment and size, avoids address zero, counts eligible slots across conventional, non-hotplug, non-soft-reserved memory bounded by min/max, optionally restricts selection to `EFI_MEMORY_MORE_RELIABLE` descriptors, maps a 32-bit seed into a target slot, walks descriptors again to find the selected slot, and allocates it with `EFI_ALLOCATE_ADDRESS`.

State and persistence behavior: mutates the temporary memory-map copy only. The chosen allocation persists to the caller as EFI pages of the requested memory type.

Dependencies and integration points: depends on EFI memory-map helpers, soft-reserve policy, `ilog2()`, and EFI page allocation. Used for physical KASLR and zboot decompressed-image placement.

Risks and test signals: if no eligible slots exist, seed multiplication with zero slots must yield an out-of-resources path. Reusing `virt_addr` is safe only on the private map copy. Test signals include mirrored memory preference, min/max bounds, alignment larger than EFI page, SP/hotplug exclusion, deterministic placement for fixed seeds, and failed exact-address allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/randomalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv-stub.c

Purpose: implements RISC-V EFI stub image sizing, optional KASLR relocation, and instruction cache synchronization for the kernel-linked EFI stub.

Important APIs/types/functions: exports `stext_offset()`, `handle_kernel_image()`, and `efi_icache_sync()`.

Control flow: `stext_offset()` returns the actual kernel text entry offset because the PE/COFF header is not part of the in-memory kernel presentation. `handle_kernel_image()` derives text/data/BSS sizes from linker symbols, sets image/reserve sizes, and calls `efi_kaslr_relocate_kernel()` with an EFI RNG physical seed. `efi_icache_sync()` emits `fence.i`.

State and persistence behavior: only updates caller-provided image and reserve addresses/sizes. Relocated memory persists to kernel entry.

Dependencies and integration points: depends on RISC-V linker symbols, common KASLR relocation, EFI RNG, and the RISC-V instruction cache fence. Used by the normal RISC-V EFI boot path.

Risks and test signals: linker symbol ranges must match actual image layout, and `fence.i` must run after copying executable code. Test signals include RISC-V EFI boot with KASLR enabled/disabled, relocation failure path, correct entry offset, and decompressed image execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv.c

Purpose: handles RISC-V EFI platform feature checks and final kernel entry ABI, especially discovery of the boot hart ID.

Important APIs/types/functions: exports `check_platform_features()`, weak `stext_offset()`, and `efi_enter_kernel()`. Internals are `get_boot_hartid_from_efi()` and `get_boot_hartid_from_fdt()`.

Control flow: platform check first tries the RISC-V EFI Boot Protocol `get_boot_hartid()`, then falls back to `/chosen/boot-hartid` in the EFI device tree. Final entry disables the MMU by clearing SATP, computes `entrypoint + stext_offset()`, and jumps with a0 = hartid and a1 = FDT address.

State and persistence behavior: static `hartid` stores boot hart discovery until final jump. No other state persists.

Dependencies and integration points: depends on EFI config-table FDT, libfdt, unaligned FDT property reads, RISC-V CSR access, and the RISC-V kernel boot ABI.

Risks and test signals: missing boot hart ID makes boot unsupported. FDT property width must be 32 or 64 bits. Test signals include EFI boot protocol presence, FDT fallback, malformed/missing `/chosen`, zboot weak offset behavior, and successful MMU-off jump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/secureboot.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/secureboot.c

Purpose: determines UEFI Secure Boot mode for the EFI stub, with shim MOK insecure-mode override handling.

Important APIs/types/functions: exports `efi_get_secureboot()`. Internal `get_var()` adapts EFI variable access to `efi_get_secureboot_mode()`.

Control flow: the function calls the generic secure-boot mode helper. If enabled, it checks shim's `MokSBStateRT` variable under `EFI_SHIM_LOCK_GUID`; a non-nonvolatile value of 1 disables secure boot from the kernel's perspective. Otherwise it logs that secure boot is enabled.

State and persistence behavior: reads EFI variables only; it does not modify state. The returned enum is stored by callers such as x86 boot params.

Dependencies and integration points: depends on EFI runtime variable access and shim variable conventions. FDT code uses the result to reject unauthenticated `dtb=` loads under secure boot.

Risks and test signals: inability to determine mode returns unknown and callers may conservatively treat it as secure. Shim variable attributes matter; nonvolatile insecure state is not honored here. Test signals include SecureBoot on/off, SetupMode-like platform states, shim insecure mode, variable read failure, and x86 `boot_params->secure_boot` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/secureboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/skip_spaces.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/skip_spaces.c

Purpose: supplies the small `skip_spaces()` helper for command-line parsing in the EFI stub.

Important APIs/types/functions: exports `skip_spaces(const char *str)`.

Control flow: advances the pointer while `isspace(*str)` is true and returns a writable `char *` cast of the resulting position.

State and persistence behavior: no state.

Dependencies and integration points: depends on Linux ctype/string types and is used by `efi_parse_options()` and other parser-style code.

Risks and test signals: behavior follows C `isspace()` on bytes; callers must pass NUL-terminated strings. Test signals include leading spaces, tabs/newlines, empty strings, and no-leading-space command lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/skip_spaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/smbios.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/smbios.c

Purpose: provides EFI-stub access to SMBIOS records and SMBIOS string fields through the EFI SMBIOS Protocol.

Important APIs/types/functions: exports `efi_get_smbios_record()` and `__efi_get_smbios_string()`. It defines a local mixed-mode `efi_smbios_protocol_t` with `get_next`.

Control flow: record lookup locates the SMBIOS protocol and requests the first record of a given type using handle `0xfffe`. String lookup walks the unformatted string table after the fixed record header until the numbered string offset is reached.

State and persistence behavior: no state is retained; returned pointers refer to firmware SMBIOS table memory.

Dependencies and integration points: depends on EFI SMBIOS Protocol and shared SMBIOS record structures in `efistub.h`. x86 Apple product matching uses these helpers.

Risks and test signals: malformed SMBIOS string tables can cause early termination; callers must validate NULL returns. Test signals include type 1 and type 4 lookups, missing protocol, missing string indexes, and mixed-mode builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/smbios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/string.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/string.c

Purpose: supplies a compact subset of string and numeric parsing routines needed by EFI stub code without the full kernel library.

Important APIs/types/functions: conditionally exports `strlen()`, `strnlen()`, `strcmp()`, `strrchr()`, and `memchr()`, and always provides `strstr()`, `strncmp()`, `simple_strtoull()`, and `simple_strtol()`.

Control flow: string routines perform straightforward byte scans. `simple_strtoull()` guesses base from `0`/`0x` prefixes when base is zero, accepts digits/letters valid for the base, and returns the end pointer. `simple_strtol()` handles a leading minus by negating the unsigned conversion.

State and persistence behavior: no state.

Dependencies and integration points: depends on ctype helpers and is used by command-line, graphics, and x86 option parsing. Optional definitions are controlled by EFI_HAVE_* and FDT parameter configs.

Risks and test signals: no overflow reporting is provided, and numeric parsing accepts only simple prefixes. Test signals include decimal/octal/hex inputs, invalid digits, negative values, substring matching, and config combinations that use arch-provided string functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/systable.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/systable.c

Purpose: provides the global EFI system table pointer definition for stub builds that need a shared `efi_system_table` object.

Important APIs/types/functions: defines `const efi_system_table_t *efi_system_table`.

Control flow: no executable flow. Architecture entry code writes this pointer before using `efi_bs_call()` or other table-based helpers.

State and persistence behavior: the pointer is process-global boot state. It remains valid until ExitBootServices for boot services and into runtime if the kernel retains runtime mappings.

Dependencies and integration points: depends on EFI type definitions and is referenced by nearly every libstub helper.

Risks and test signals: duplicate definitions are architecture-sensitive; x86 provides its own definition. Test signals are link success for each EFI stub target and early entry setting the pointer before any helper call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/systable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/tpm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/tpm.c

Purpose: handles EFI reset-attack mitigation and copies TPM2/TCG1.2/Confidential Computing event logs into a Linux EFI configuration table for the kernel.

Important APIs/types/functions: conditionally exports `efi_enable_reset_attack_mitigation()` and always exports `efi_retrieve_eventlog()`. Internal `efi_retrieve_tcg2_eventlog()` calculates event-log size and handles final-events-table accounting.

Control flow: reset mitigation checks the MemoryOverwriteRequestControl variable and sets it to request memory clearing on next reboot. Event-log retrieval first tries TCG2 protocol with TCG2 format, falls back to TCG1.2 format, or uses the CC measurement protocol. It calculates the final entry size, optionally totals preboot final events, allocates ACPI reclaim memory, copies the log, records version and sizes, and installs `LINUX_EFI_TPM_EVENT_LOG_GUID`.

State and persistence behavior: the copied event log persists as an EFI configuration table. Reset mitigation writes a nonvolatile/runtime EFI variable when supported.

Dependencies and integration points: depends on EFI TCG2, EFI CC Measurement Protocol, TPM event-log size helpers, final events tables, EFI variables, and configuration-table install. Common and x86 stubs call it before ExitBootServices.

Risks and test signals: malformed event logs can produce zero event sizes; firmware may return only last-entry pointers; final-events parsing depends on the first log entry's algorithms. Test signals include TPM2 logs, TCG1.2 fallback, CC logs, empty logs, final-events preboot size, allocation failure, and MemoryOverwriteRequestControl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/tpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/unaccepted_memory.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/unaccepted_memory.c

Purpose: creates and maintains the Linux EFI unaccepted-memory bitmap used by confidential-computing guests to defer memory acceptance until first use.

Important APIs/types/functions: exports `allocate_unaccepted_bitmap()`, `process_unaccepted_memory()`, and `accept_memory()`. Uses global `struct efi_unaccepted_memory *unaccepted_table`.

Control flow: allocation checks for an existing table, scans EFI memory descriptors for `EFI_UNACCEPTED_MEMORY`, computes the aligned covered physical range and bitmap size, allocates ACPI reclaim memory, initializes version/base/unit/size, and installs `LINUX_EFI_UNACCEPTED_MEM_TABLE_GUID`. Processing accepts too-small or unaligned edge pieces immediately, clamps to bitmap coverage, accepts out-of-bitmap ranges, and marks aligned 2 MiB units. Later `accept_memory()` maps a physical range to bitmap bits, calls `arch_accept_memory()` for set ranges, and clears those bits.

State and persistence behavior: the unaccepted table and bitmap persist into kernel boot through an EFI configuration table. Bitmap bits are mutable and track unaccepted ranges until accepted.

Dependencies and integration points: depends on EFI unaccepted memory descriptor type, bitmap helpers, architecture `arch_accept_memory()`, and x86 e820 setup calling `process_unaccepted_memory()`.

Risks and test signals: granularity can force immediate acceptance of small/unaligned ranges, and bitmap sizing must not under-cover high physical holes. Test signals include no-unaccepted-memory boot, preinstalled table version check, unaligned start/end ranges, ranges below/above bitmap coverage, repeated acceptance clearing bits, and SEV/TDX guest boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/unaccepted_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/vsprintf.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/vsprintf.c

Purpose: implements a compact `vsnprintf()`/`snprintf()` for EFI stub diagnostics without relying on the full kernel formatter.

Important APIs/types/functions: exports `vsnprintf()` and `snprintf()`. Internal helpers parse flags/width/precision/qualifiers, format 64-bit decimal without division-heavy operations, handle octal/hex/pointers, and convert UTF-16 wide strings/chars to UTF-8.

Control flow: the formatter copies literal characters, parses `%` conversions, obtains field widths and precision from digits or `*`, supports `h/hh/l/ll`, handles `%c`, `%lc`, `%s`, `%ls`, `%o`, `%p`, `%x`, `%X`, `%d`, `%i`, and `%u`, applies sign/prefix/padding rules, writes bounded output through `PUTC`, and stops on invalid specifiers.

State and persistence behavior: no persistent state. It operates on caller buffers and returns the untruncated output length.

Dependencies and integration points: depends on local string helpers and is used by `efi_printk()` and other stub formatting.

Risks and test signals: unsupported format specifiers abort remaining formatting, wide-string length accounting must avoid partial UTF-8 writes, and return type is `int` despite `size_t` internal position. Test signals include integer formats with flags/precision, pointers, width from `*`, UTF-16 BMP and surrogate pairs, NULL strings, buffer size 0/1, and invalid specifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/vsprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-5lvl.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-5lvl.c

Purpose: supports enabling or disabling x86 5-level paging during EFI stub boot by preparing a 32-bit trampoline and switching CR3/CR4 state before kernel entry.

Important APIs/types/functions: exports global `efi_no5lvl`, `efi_setup_5level_paging()`, and `efi_5level_switch()`. Uses external trampoline symbols `trampoline_32bit_src` and `trampoline_ljmp_imm_offset`.

Control flow: setup only runs on 64-bit firmware with CPUID LA57 support. It allocates two 32-bit-addressable pages, copies the trampoline, pads it, fixes the absolute long-jump target, and adjusts memory protections. The switch function compares desired LA57 state with current CR4, builds or selects a 32-bit-addressable root page table, loads a small GDT, and invokes the trampoline.

State and persistence behavior: static `la57_toggle` points to allocated trampoline code and adjacent page table memory. `efi_no5lvl` is set by command-line parsing.

Dependencies and integration points: depends on CPUID, x86 GDT/CR3/CR4 helpers, EFI low memory allocation, memory protection adjustment, and x86 stub final handoff.

Risks and test signals: the trampoline and root page table must be below 4 GiB, the LJMP fixup must be correct, and toggling LA57 is only valid from 32-bit mode with paging disabled. Test signals include LA57-capable and non-capable machines, `no5lvl`, firmware already in LA57, high root table copy, and successful kernel entry after toggle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-5lvl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.c

Purpose: implements the x86 EFI boot stub entry path, including boot_params allocation, command-line parsing, kernel decompression and placement, initrd handling, secure boot/RNG/TPM/GOP/PCI/Apple quirks, unaccepted memory setup, e820 construction, ExitBootServices, SEV setup, optional 5-level paging switch, and final jump.

Important APIs/types/functions: defines `efi_pe_entry()`, optional handover entries, `efi_stub_entry()`, `efi_adjust_memory_range_protection()`, and many x86 helpers such as `setup_e820()`, `exit_boot()`, `efi_decompress_kernel()`, `setup_efi_pci()`, `retrieve_apple_device_properties()`, and `setup_unaccepted_memory()`.

Control flow: entry validates the EFI system table, allocates boot params if not handed over, rejects unsupported SNP features, locates DXE services and Memory Attribute Protocol, prepares 5-level paging trampoline, parses built-in and loader command lines, propagates memory encryption flags, decompresses the kernel into randomized or bounded memory, loads initrd and updates boot params, records secure boot, reset mitigation, RNG seed, TPM log, graphics, PCI ROM setup data, Apple quirks, and unaccepted memory policy. It then exits boot services, fills EFI info and e820/e820ext from the final memory map, enables SEV while firmware exception state is still active, toggles 5-level paging if needed, and jumps to the decompressed kernel with boot params in RSI/ESI.

State and persistence behavior: global `efi_system_table`, `efi_dxe_table`, `image`, `memattr`, `cmdline_memmap_override`, boot params, setup_data chains, initrd table, e820 entries, unaccepted memory bitmap, and copied PCI/Apple data persist into kernel entry. Hardware/firmware state changes include memory attributes, boot-services exit, SEV enable, PCI bus-master changes, and possible paging mode toggle.

Dependencies and integration points: depends on x86 decompressor symbols/functions, EFI boot/file/GOP/PCI/Apple/DXE/Memory Attribute protocols, e820 types, SEV/SNP helpers, KASLR RNG, common initrd/random/TPM/secureboot helpers, and x86 boot ABI.

Risks and test signals: high-risk areas include decompression placement under `mem=`/`memmap=`/`hugepages=`, firmware memory protection quirks, Apple-specific protocol handling, e820 extension sizing, unaccepted memory table creation, ExitBootServices retry, SEV/SNP feature compatibility, and mixed handover/PE paths. Test signals include x86_32/x86_64/mixed-mode builds, handover protocol, KASLR on/off and AMI v2 quirk, external initrd override, secure boot, TPM event log, GOP/EDID, PCI option ROM preservation, e820ext overflow, SEV-SNP guests, and LA57 transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.h

Purpose: declares x86 EFI stub interfaces shared between the main x86 stub and 5-level paging support.

Important APIs/types/functions: declares trampoline symbols, `efi_adjust_memory_range_protection()`, and `efi_setup_5level_paging()`/`efi_5level_switch()` with no-op stubs on non-64-bit builds.

Control flow: no direct flow. It provides compile-time selection between real LA57 support on x86_64 and no-op behavior elsewhere.

State and persistence behavior: no state in the header.

Dependencies and integration points: depends on EFI and x86 boot headers. It connects `x86-stub.c` to `x86-5lvl.c`.

Risks and test signals: incorrect conditional prototypes would break 32-bit or 64-bit EFI builds. Test signals are successful x86_32, x86_64, `CONFIG_EFI_MIXED`, and non-LA57 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-gzip.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-gzip.c

Purpose: provides gzip payload decompression for EFI zboot images.

Important APIs/types/functions: exports `efi_zboot_decompress_init()` and `efi_zboot_decompress()`. Uses zlib inflate sources included directly and a static `z_stream_s`.

Control flow: init skips the fixed 10-byte gzip header, sets input bounds, allocates zlib workspace through EFI pages, initializes raw deflate mode with `-MAX_WBITS`, and returns the uncompressed payload size. Decompress sets output pointers, runs inflate, ends the stream, frees workspace, checks for `Z_STREAM_END`, syncs instruction cache, and returns EFI status.

State and persistence behavior: static stream/workspace state exists between init and decompress only. The decompressed output buffer persists to common stub boot.

Dependencies and integration points: depends on zlib, EFI page allocation/free, linker symbols for compressed data and payload size, and arch `efi_cache_sync_image()`.

Risks and test signals: assumes no gzip filename/extra header beyond 10 bytes and exactly one init/decompress sequence. Test signals include valid gzip zboot, corrupt payload, workspace allocation failure, cache sync, and payload-size consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-gzip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-zstd.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-zstd.c

Purpose: provides Zstandard payload decompression for EFI zboot images.

Important APIs/types/functions: exports `efi_zboot_decompress_init()` and `efi_zboot_decompress()`. Uses Zstd decompressor workspace tracked in static `wksp_size` and `wksp`.

Control flow: init computes workspace bound, allocates EFI pages, and returns `payload_size`. Decompress initializes a Zstd context in that workspace, decompresses from `_gzdata_start` to `_gzdata_end - 4`, frees the workspace, checks the Zstd error code, syncs the instruction cache, and reports EFI load errors on failure.

State and persistence behavior: workspace state is transient between init and decompress. Output buffer persists to zboot common boot.

Dependencies and integration points: depends on Linux Zstd decompressor sources, EFI page allocation/free, compressed payload linker symbols, and arch cache sync.

Risks and test signals: the `- 4` input-size adjustment must match zboot payload layout, and workspace must not be reused after free. Test signals include valid/corrupt Zstd images, allocation failure, payload size checks, and instruction-cache coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-zstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-header.S -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-header.S

Purpose: emits the EFI PE/COFF and Linux zboot image header for compressed EFI boot images, including payload metadata, optional SBAT, optional debug directory, and section table layout.

Important APIs/types/functions: defines global `__efistub_efi_zboot_header` in `.head`, DOS/zimg metadata fields, PE header, optional header, data directories, `.text`, optional `.sbat`, and `.data` section headers, and optional CodeView/extended DLL characteristics records.

Control flow: assembly is declarative. Firmware reads the PE/COFF header to load the zboot EFI application, while Linux/zboot tooling can read the `zimg` fields for payload offset, payload size, and `COMP_TYPE`.

State and persistence behavior: creates immutable image-header data in the binary. It does not maintain runtime state.

Dependencies and integration points: depends on PE constants, architecture `MACHINE_TYPE`, 32/64-bit config, `COMP_TYPE`, compressed-data linker symbols, SBAT config, debug EFI path config, and zboot entry symbol.

Risks and test signals: header offsets, section sizes, file alignment, payload size subtraction, and optional table sizes must match linker output. Test signals include firmware loading the zboot image, PE inspection, Secure Boot/SBAT validation, debug table presence under config, and decompressor locating `_gzdata_start`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot.c

Purpose: implements the EFI zboot entry point that decompresses a compressed kernel payload into EFI memory and then runs the shared EFI stub common path on the decompressed image.

Important APIs/types/functions: exports weak `efi_cache_sync_image()`, `alloc_primary_display()`, and `efi_zboot_entry()`. Internal `alloc_preferred_address()` tries an architecture preferred kernel image address.

Control flow: entry records the EFI system table, obtains Loaded Image Protocol, handles command line/options, initializes decompressor to get allocation size, tries preferred address, otherwise obtains RNG seed when KASLR is enabled and uses `efi_random_alloc()`, decompresses into the allocation, calls `efi_stub_common()`, and frees the allocation on return/failure.

State and persistence behavior: writes global `efi_system_table`; image allocation persists only until common stub returns, but successful boot does not return. Primary display allocation is routed through the config-table approach.

Dependencies and integration points: depends on zboot decompressor backends, EFI Loaded Image Protocol, common command-line and stub code, random allocation, arch image alignment/cache hooks, and optional preferred address.

Risks and test signals: allocation must match decompressed payload size and alignment, RNG failures disable KASLR, and returned failure must free the decompressed image. Test signals include gzip/zstd zboot, preferred address success/failure, KASLR disabled/enabled, EFI_RNG unavailable, and handoff through common stub with initrd/FDT/GOP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/memattr.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/memattr.c

Purpose: validates, reserves, and applies the EFI Memory Attributes Table so runtime service mappings can be tightened with firmware-provided permissions.

Important APIs/types/functions: exports `efi_memattr_init()` and `efi_memattr_apply_permissions()`. Internal `entry_is_valid()` verifies table descriptors against the EFI memory map and computes virtual addresses.

Control flow: early init maps the table header, rejects unexpected versions/descriptors/counts, reserves the full table with memblock, and sets `EFI_MEM_ATTR`. Permission application memremaps the full table, detects BTI/forward-control-flow-guard support, iterates entries, validates runtime code/data coverage against current EFI memmap virtual addresses, logs invalid entries, and calls the architecture-provided permission setter until failure.

State and persistence behavior: global `efi_mem_attr_table` holds the physical address and `tbl_size` stores validated size. Reserved table memory persists for runtime permission setup.

Dependencies and integration points: depends on early memremap/memblock, EFI memory map, `efi_memattr_perm_setter`, architecture page-table permission code, and EFI flags.

Risks and test signals: corrupted table sizes can exhaust memory without caps, descriptors may not align to kernel page size, and missing virtual addresses mean no stub virtual map was installed. Test signals include valid/invalid table versions, descriptor size mismatches, more than 64k entries, runtime code/data permission changes, BTI flag propagation, and kexec-loaded maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/memattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/memmap.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/memmap.c

Purpose: maps, unmaps, and remaps the kernel's persistent EFI memory map representation during early and late boot.

Important APIs/types/functions: exports `__efi_memmap_init()`, `efi_memmap_init_early()`, `efi_memmap_unmap()`, and `efi_memmap_init_late()`.

Control flow: common init chooses `early_memremap()` or `memremap()` based on `EFI_MEMMAP_LATE`, fills `efi.memmap` fields, computes entry count and end pointer, and sets the `EFI_MEMMAP` flag. Early init clears flags and maps via early remap. Unmap chooses early or late unmap and clears state. Late init asserts early mapping was removed, copies descriptor metadata from the prior map, and remaps the physical map with `memremap()`.

State and persistence behavior: global `efi.memmap` and `efi.flags` are updated. The late mapping persists for runtime services and EFI descriptor lookups.

Dependencies and integration points: depends on early ioremap, memremap, EFI global state, and runtime setup code such as RISC-V's `riscv_enable_runtime_services()`.

Risks and test signals: forgetting to unmap early fixmap space, descriptor metadata mismatch, and failed remap leave EFI runtime support degraded. Test signals include early map success, unmap idempotence, late remap after vmalloc setup, EFI_MEMMAP flag transitions, and `efi_mem_desc_lookup()` after late mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/memmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/mokvar-table.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/mokvar-table.c

Purpose: validates a Linux EFI Machine Owner Key variable configuration table, reserves it, maps it for runtime kernel use, provides table iteration/search helpers, and exposes entries under `/sys/firmware/efi/mok-variables/`.

Important APIs/types/functions: exports `efi_mokvar_table_init()`, `efi_mokvar_entry_next()`, and `efi_mokvar_entry_find()`. Internal sysfs path uses `efi_mokvar_sysfs_read()` and `efi_mokvar_sysfs_init()`, with `struct efi_mokvar_sysfs_attr` list nodes.

Control flow: early init requires an EFI memmap and valid table physical address, verifies the table lies within one EFI memory descriptor, walks variable-size entries until a sentinel with empty name and zero data size, enforces name NUL termination, remaps headers as needed across pages, reserves boot-services memory, and records total size. Fs init memremaps the whole table, creates the `mok-variables` kobject, creates one read-only binary sysfs attribute per entry, and stores attributes in a permanent list. Reads require `CAP_SYS_ADMIN` and copy bounded entry data.

State and persistence behavior: `efi_mokvar_table_size`, `efi_mokvar_table_va`, `efi_mokvar_sysfs_list`, and `mokvar_kobj` persist after init. The table memory is reserved and mapped read-only to users via sysfs.

Dependencies and integration points: depends on EFI MOK config table discovery, EFI memory map lookup/reservation, early and late memremap, sysfs/kobject APIs, capabilities, and certificate-loading code that can query entries.

Risks and test signals: there is no table header, so validation must avoid walking outside one descriptor. Sysfs init error paths can leave mappings/kobjects partially present. Test signals include valid sentinel tables, malformed data sizes, tables crossing descriptors, boot-services reservation, entry find/iteration, CAP_SYS_ADMIN reads, and absence of table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/mokvar-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/ovmf-debug-log.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/ovmf-debug-log.c

Purpose: maps an OVMF debug log buffer advertised through EFI and exposes it as `/sys/firmware/efi/ovmf_debug_log`.

Important APIs/types/functions: exports `ovmf_log_probe()`. Internal `struct ovmf_debug_log_header` describes ring-buffer metadata and `ovmf_log_read()` implements binary sysfs reads.

Control flow: probe maps the header, validates two magic values, logs firmware version and buffer size, remaps the full header+log buffer, sets `logbuf` and `logbufsize`, sets sysfs bin attribute size, and registers the binary file. Reads compute ring-buffer start/end from head/tail offsets, handle wraparound, clamp to log and tail bounds, and copy available bytes.

State and persistence behavior: static `hdr`, `logbuf`, and `logbufsize` hold the mapped firmware buffer for the kernel lifetime unless probe fails and unmaps. The sysfs file exposes live firmware log memory.

Dependencies and integration points: depends on EFI table discovery by caller, memremap, EFI kobject, and sysfs binary attributes. Intended for OVMF/EDK2 debug firmware.

Risks and test signals: header fields are trusted after magic validation; bad offsets can make reads return zero or expose truncated data. Attribute size is header+log size while read addresses log bytes, so offsets need careful user expectations. Test signals include valid/invalid magic, wrapped and non-wrapped buffers, truncated flag scenarios, sysfs registration failure, and bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/ovmf-debug-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/rci2-table.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/rci2-table.c

Purpose: validates a Dell Runtime Configuration Interface v2 EFI table and exposes it as a read-only admin sysfs binary file under `/sys/firmware/efi/tables/rci2`.

Important APIs/types/functions: uses `struct rci2_table_global_hdr`, global `rci2_table_phys`, static `checksum()`, and late init `efi_rci2_sysfs_init()`. The sysfs attribute is created with `BIN_ATTR_SIMPLE_ADMIN_RO(rci2)`.

Control flow: late init skips absent tables, maps the header, checks `_RC_` signature, reads full table length, remaps the full table, verifies 16-bit additive checksum equals zero, creates the `tables` kobject, attaches the mapped table as private data, and creates the binary sysfs file.

State and persistence behavior: `rci2_table_phys` is set during EFI table discovery elsewhere; `rci2_base` remains memremapped after successful sysfs creation and backs reads. No mutable runtime state exists after init.

Dependencies and integration points: depends on EFI kobject, memremap, sysfs, and firmware-provided RCI2 table address. User space consumes the binary table.

Risks and test signals: table length is read from firmware after only header mapping, so bogus lengths can cause remap failure. Checksum handles odd byte lengths. Test signals include absent table, bad signature, zero length, bad checksum, odd-length checksum, sysfs file size/content, and kobject creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/rci2-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/reboot.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/reboot.c

Purpose: routes system reboot and optional poweroff through EFI ResetSystem runtime services, honoring firmware quirks and pending capsule update reset requirements.

Important APIs/types/functions: exports `efi_reboot()`, weak `efi_poweroff_required()`, and global `efi_reboot_quirk_mode`. Internal `efi_power_off()` and `efi_shutdown_init()` register a sys-off handler when needed.

Control flow: reboot first checks ResetSystem support, maps Linux reboot mode to EFI warm/cold, applies quirk override, checks pending capsule update reset mode and logs if it changes the requested reset type, then calls `efi.reset_system()`. Late init registers an EFI shutdown handler before ACPI poweroff if the architecture/platform requires EFI poweroff.

State and persistence behavior: `efi_reboot_quirk_mode` can be set by platform quirks. `efi_sys_off_handler` stores the registered poweroff handler.

Dependencies and integration points: depends on EFI runtime service wrappers, capsule update state, Linux reboot/sys-off framework, and platform overrides of `efi_poweroff_required()`.

Risks and test signals: ResetSystem may not return but firmware failures can leave system running. Capsule reset mode must override user-requested warm/cold resets. Test signals include warm/cold reboot, quirk-forced modes, pending capsule update, unsupported runtime reset service, and EFI-required poweroff systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/riscv-runtime.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/riscv-runtime.c

Purpose: enables RISC-V EFI runtime services by remapping the EFI memory map, creating runtime page-table mappings, applying EFI memory attributes, wiring runtime service wrappers, and switching address spaces around EFI calls.

Important APIs/types/functions: internal `efi_virtmap_init()` and `riscv_enable_runtime_services()` perform setup. Exports `arch_efi_call_virt_setup()` and `arch_efi_call_virt_teardown()` for runtime wrappers. `riscv_dmi_init()` initializes DMI early.

Control flow: early init verifies EFI boot, unmaps the early memory map, remaps it late, registers soft-reserved EFI memory resources, exits if runtime services are disabled or paravirtualized, allocates and initializes `efi_mm`, maps all runtime descriptors unless any has `virt_addr == U64_MAX`, applies memattr permissions, calls `efi_native_runtime_setup()`, and sets `EFI_RUNTIME_SERVICES`. Runtime call setup syncs kernel mappings, disables preemption, switches to `efi_mm`; teardown switches back and enables preemption.

State and persistence behavior: `efi_mm` persists as the EFI runtime address space. Soft-reserved resources are inserted into `iomem_resource`. EFI flags record runtime availability.

Dependencies and integration points: depends on EFI memmap/memattr code, RISC-V page-table mapping helpers, scheduler MM switching, resource tree, DMI setup, and generic runtime wrappers.

Risks and test signals: missing virtual addresses disable runtime services, mapping failures leave services unavailable, and address-space switching must restore preemption/MM state reliably. Test signals include RISC-V EFI boot, runtime variable reads/writes, soft-reserve resources, memattr permission application, runtime-disabled command line, paravirt runtime mode, and DMI data availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/riscv-runtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/runtime-wrappers.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/runtime-wrappers.c

Purpose: serializes and safely dispatches EFI runtime service calls through a workqueue-backed wrapper layer, providing kernel-facing `efi.*` runtime operations.

Important APIs/types/functions: exports `efi_call_virt_save_flags()`, `efi_call_virt_check_flags()`, `efi_native_runtime_setup()`, optional `efi_call_acpi_prm_handler()`, and `efi_runtime_assert_lock_held()`. Central types are `union efi_rts_args`, global `efi_rts_work`, `efi_runtime_lock`, and `efi_runtime_lock_owner`.

Control flow: callers enter wrapper functions such as `virt_efi_get_variable()` or `virt_efi_set_time()`, take the binary semaphore, populate `efi_rts_work`, queue work to `efi_rts_wq`, and wait for completion. The work function switches to architecture EFI runtime calling context, saves IRQ flags, dispatches the selected runtime service, checks/restores corrupted IRQ flags, stores status, completes, and clears lock ownership. Nonblocking variable operations use `down_trylock()` and direct virtual calls for interrupt-sensitive users. ResetSystem uses trylock and direct call because it may not return.

State and persistence behavior: global work object and semaphore serialize all runtime calls. `efi_native_runtime_setup()` installs wrapper function pointers into global `efi`. Lock ownership is tracked for assertions and UV platform aliases the lock when configured.

Dependencies and integration points: depends on EFI runtime tables, `efi_rts_wq`, completions/workqueues, architecture `arch_efi_call_virt_setup()/teardown()`, IRQ flag handling, pstore/variable users, capsule update users, reset/reboot paths, and optional ACPI PRMT.

Risks and test signals: all queued calls share one global work object, so serialization is mandatory. Firmware can corrupt IRQ flags, runtime calls can block, nonblocking paths can fail with `EFI_NOT_READY`, and ResetSystem lock contention prevents reset. Test signals include concurrent variable/time/capsule calls, pstore nonblocking set-variable, runtime services disabled, firmware IRQ flag corruption warnings, reset path, ACPI PRM handler, and lock-held assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/runtime-wrappers.c -->
