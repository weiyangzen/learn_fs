# subset-b-001287 research

This grouped report covers DMI/EDD firmware discovery and EFI core, capsule, CPER, ESRT, pstore, Apple-property, early console, FDT, and selected EFI libstub sources under the assigned Ceph-client source mirror. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi_scan.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/dmi_scan.c

Purpose: discovers SMBIOS/DMI tables early in boot, extracts stable system identity fields, exposes raw DMI data under `/sys/firmware/dmi/tables`, and provides exported match/query helpers used by quirks, drivers, and RAS code.

Important APIs/types/functions: exported symbols include `dmi_kobj`, `dmi_available`, `dmi_string_nosave()`, `dmi_check_system()`, `dmi_first_match()`, `dmi_get_system_info()`, `dmi_name_in_vendors()`, `dmi_find_device()`, `dmi_get_date()`, `dmi_get_bios_year()`, `dmi_walk()`, `dmi_match()`, and memory-device helpers `dmi_memdev_name()`, `dmi_memdev_size()`, `dmi_memdev_type()`, and `dmi_memdev_handle()`. Internal parsing is centered on `dmi_decode_table()`, `dmi_present()`, `dmi_smbios3_present()`, `dmi_scan_machine()`, and `dmi_decode()`.

Control flow: `dmi_setup()` calls `dmi_scan_machine()` before many arch/driver init consumers need DMI data. The scanner prefers EFI SMBIOS3, falls back to EFI legacy SMBIOS, then optionally scans the legacy physical window. Valid entry points set `dmi_base`, `dmi_len`, `dmi_num`, and `dmi_ver`, then walk the table with `dmi_decode()` to save BIOS, system, board, chassis, OEM string, onboard device, slot, IPMI, and extended device data. `dmi_memdev_walk()` makes a second pass for type-17 memory-device records. Later, `subsys_initcall(dmi_init)` creates sysfs binary files for the entry point and table.

State and persistence behavior: DMI identity strings, device lists, table base/length, SMBIOS entry-point bytes, and memory-device arrays are retained in kernel memory after early parsing. Raw table sysfs data is backed by a remapped DMI table and persists while the firmware sysfs tree exists; there is no dynamic rescan.

Dependencies and integration points: depends on architecture DMI remap helpers, EFI config-table addresses, memblock/DMI allocators, sysfs firmware kobjects, random seeding via `add_device_randomness()`, and `include/linux/dmi.h` match structures. CPER memory-error reporting uses the memory-device lookup helpers.

Risks and test signals: firmware tables are untrusted, so length checks, checksums, short-entry detection, end-of-table handling, and bounds-limited string walking are critical. Watch for malformed SMBIOS versions, bad physical addresses, and duplicate/empty device strings. Test signals include boot logs reporting SMBIOS version and identity, populated `/sys/firmware/dmi/tables/{smbios_entry_point,DMI}`, successful DMI quirk matches, and memory-error DIMM location decoding using type-17 handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/edd.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/edd.c

Purpose: exports BIOS Enhanced Disk Drive data collected during x86 setup through `/sys/firmware/edd/int13_devXX`, making INT 13h disk parameters, MBR signatures, geometry, and EDD 3.0 path information visible to userspace.

Important APIs/types/functions: defines private `struct edd_device` and `struct edd_attribute`. Attribute show/test helpers include `edd_show_raw_data()`, `edd_show_version()`, `edd_show_extensions()`, `edd_show_info_flags()`, `edd_show_sectors()`, legacy/default geometry show functions, `edd_show_interface()`, `edd_show_host_bus()`, and presence validators such as `edd_has_edd30()`. Device lifecycle is handled by `edd_device_register()`, `edd_populate_dir()`, `edd_device_unregister()`, `edd_release()`, `edd_init()`, and `edd_exit()`.

Control flow: `late_initcall(edd_init)` exits if setup code found no EDD or MBR-signature entries. It creates the `edd` kset below `firmware_kobj`, allocates one `edd_device` per BIOS disk slot, binds it to global `edd` setup data, creates only attributes whose test callbacks pass, optionally links `pci_dev` for PCI/XPRS devices, and emits a kobject add event. Module exit drops kobject refs and unregisters the kset.

State and persistence behavior: per-device state stores the device index, optional MBR signature, pointer into the global `edd.edd_info[]` array, and kobject. The driver does not persist anything itself; it publishes boot-time BIOS data until module removal or shutdown.

Dependencies and integration points: depends on `linux/edd.h` boot-time data, sysfs/kobject APIs, firmware kobject, PCI device lookup for host-bus paths, and block/firmware userspace tooling that consumes EDD metadata.

Risks and test signals: BIOS data is legacy and often imperfect; `edd_has_edd30()` checks key, path length, and checksum before exposing host/interface fields, and raw-data size is clamped to the known structure size. There is limited rollback for partial sysfs file creation. Test signals are correct `int13_dev80+` directories, conditional absence of invalid attributes, PCI symlink creation where applicable, and clean teardown with no leaked kobjects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/edd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/Kconfig

Purpose: defines EFI firmware feature switches for ESRT, efivars pstore, special-purpose memory reservation, DXE memory attributes, FDT-derived parameters, runtime wrappers, generic/zboot stubs, DTB loader, bootloader control, capsule loader, EFI tests, Apple properties, reset attack mitigation, RCI2 table support, early PCI DMA disabling, and EFI early console.

Important APIs/types/functions: Kconfig symbols include `EFI_ESRT`, `EFI_VARS_PSTORE`, `EFI_VARS_PSTORE_DEFAULT_DISABLE`, `EFI_SOFT_RESERVE`, `EFI_DXE_MEM_ATTRIBUTES`, `EFI_PARAMS_FROM_FDT`, `EFI_RUNTIME_WRAPPERS`, `EFI_GENERIC_STUB`, `EFI_ZBOOT`, `EFI_ARMSTUB_DTB_LOADER`, `EFI_BOOTLOADER_CONTROL`, `EFI_CAPSULE_LOADER`, `EFI_CAPSULE_QUIRK_QUARK_CSH`, `EFI_TEST`, `EFI_DEV_PATH_PARSER`, `APPLE_PROPERTIES`, `RESET_ATTACK_MITIGATION`, `EFI_RCI2_TABLE`, `EFI_DISABLE_PCI_DMA`, and `EFI_EARLYCON`.

Control flow: no runtime control flow. The symbols select objects in the EFI Makefiles, enable boot-stub paths, and gate runtime services, sysfs, pstore, capsule, and platform quirk features.

State and persistence behavior: state is build configuration persisted in `.config`; it determines which EFI facilities exist in the built kernel or modules.

Dependencies and integration points: integrates with global `EFI`, `EFI_STUB`, `PSTORE`, `ACPI_HMAT`, `X86`, architecture-selected `EFI_PARAMS_FROM_FDT`, `UCS2_STRING`, and EFI runtime/device-path consumers.

Risks and test signals: risky options include capsule loading, runtime tests, reset attack mitigation, DXE memory attribute changes, and early PCI busmaster disabling because they depend heavily on firmware behavior. Test signals are matrix builds for symbol combinations and runtime visibility of `/sys/firmware/efi`, `/dev/efi_capsule_loader`, pstore backend registration, and early console behavior when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/Makefile

Purpose: wires EFI core, optional table/sysfs/runtime facilities, architecture runtime setup, capsule loading, CPER decoders, early console, and libstub into Kbuild.

Important APIs/types/functions: builds core `efi.o`, `vars.o`, `reboot.o`, `memattr.o`, `tpm.o`, and `memmap.o` for `CONFIG_EFI`; conditionally adds `efi-bgrt.o`, `capsule.o`, `capsule-loader.o`, `fdtparams.o`, `esrt.o`, `efi-pstore.o`, `cper*.o`, `runtime-wrappers.o`, `efibc.o`, `dev-path-parser.o`, `apple-properties.o`, `embedded-firmware.o`, `mokvar-table.o`, `ovmf-debug-log.o`, `sysfb_efi.o`, architecture runtime files, and `libstub`.

Control flow: no runtime flow. Kbuild selection determines which initcalls and exported symbols exist. The Makefile also disables KASAN instrumentation for `runtime-wrappers.o` on ARM64 because EFI runtime mappings lack KASAN shadow.

State and persistence behavior: none beyond build products.

Dependencies and integration points: mirrors the EFI Kconfig feature graph and architecture symbols. It connects generic EFI core code to ARM/ARM64/RISC-V runtime enablement and to the EFI boot stub subdirectory.

Risks and test signals: incorrect object gating can produce missing symbols or dead code under architecture-specific configs. Test signals are allmodconfig/defconfig builds across x86, ARM, ARM64, and RISC-V, plus link checks for capsule/CPER/pstore combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/apple-properties.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/apple-properties.c

Purpose: imports Apple Mac EFI device properties passed through x86 setup data and attaches them to Linux devices as software nodes, enabling drivers to consume firmware-provided properties such as GPU or Thunderbolt metadata.

Important APIs/types/functions: private wire formats are `struct properties_header` and `struct dev_header`. Main helpers are `map_properties()`, `unmarshal_devices()`, `unmarshal_key_value_pairs()`, and the `dump_apple_properties` boot option handler.

Control flow: `fs_initcall(map_properties)` runs only on `x86_apple_machine`. It walks the `setup_data` chain for `SETUP_APPLE_PROPERTIES`, maps the header and payload, validates version and length, parses each EFI device path with `efi_get_device_by_path()`, allocates `property_entry` arrays, converts UCS-2 property names to UTF-8, and calls `device_create_managed_software_node()`. After processing, it clears payload length and frees the payload memory via memblock while preserving the setup-data chain header.

State and persistence behavior: parsed properties become managed software nodes owned by each device. The original setup payload is freed after import. Optional dump mode emits property names and hex data to the log.

Dependencies and integration points: depends on x86 boot params, Apple platform detection, EFI device path parser, Linux device property API, UCS-2 conversion, memblock, and devices being instantiated by fs initcall time.

Risks and test signals: malformed lengths, unsupported device-path nodes, and missing devices cause property loss for that entry. Key names are heap-allocated and freed after software-node creation, so managed-node copy semantics are essential. Test signals include `dump_apple_properties` logs, successful software node creation on Mac hardware, and driver-visible properties through `device_property_read_*()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/apple-properties.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/arm-runtime.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/arm-runtime.c

Purpose: enables EFI runtime services on ARM and ARM64 after early memory setup by remapping EFI runtime regions into a dedicated `efi_mm` page table and installing native runtime service pointers.

Important APIs/types/functions: core functions are `efi_virtmap_init()`, `arm_enable_runtime_services()`, `efi_virtmap_load()`, `efi_virtmap_unload()`, and `arm_dmi_init()`. Optional ptdump support registers `efi_page_tables`.

Control flow: `early_initcall(arm_enable_runtime_services)` checks EFI boot status, unmaps the early memory map, remaps it late, installs soft-reserved resource entries for EFI specific-purpose memory, honors `efi=noruntime`/runtime-disabled state, and skips setup if paravirtual runtime services are already active. Otherwise it builds page-table mappings for every `EFI_MEMORY_RUNTIME` descriptor with valid virtual addresses, applies EFI memory-attribute permissions, calls `efi_native_runtime_setup()`, and sets `EFI_RUNTIME_SERVICES`. `efi_virtmap_load/unload()` switch page tables around runtime calls with preemption disabled.

State and persistence behavior: `efi_mm` page tables persist for runtime calls. Soft-reserved resources are inserted in `iomem_resource`. Runtime availability is reflected in `efi.flags`.

Dependencies and integration points: depends on EFI memory map infrastructure, architecture page-table helpers, `efi_memattr_apply_permissions()`, native runtime wrappers, memblock/iomem resources, and DMI setup for ARM platforms.

Risks and test signals: missing runtime virtual addresses, failed mappings, or invalid memory attributes disable runtime services. Page-table switching must be balanced and non-preemptible. Test signals include EFI runtime variables/time access on ARM/ARM64, `efi_page_tables` debugfs output when enabled, and DMI availability before DMI ID init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/arm-runtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule-loader.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule-loader.c

Purpose: implements `/dev/efi_capsule_loader`, a misc character device that accepts an EFI capsule image from userspace and submits it to firmware through the EFI capsule core.

Important APIs/types/functions: key routines are `efi_capsule_open()`, `efi_capsule_write()`, `efi_capsule_release()`, `efi_capsule_submit_update()`, weak `efi_capsule_setup_info()`, shared `__efi_capsule_setup_info()`, and `efi_free_all_buff_pages()`. It uses `struct capsule_info` from EFI headers.

Control flow: each open allocates a fresh capsule state with arrays for pages and physical addresses. Writes must be sequential; data is copied page by page from userspace. Once enough bytes are available for the header, `efi_capsule_setup_info()` copies header fields, validates firmware support via `efi_capsule_supported()`, determines total size, and resizes page/phys arrays. When `count >= total_size`, the pages are optionally `vmap()`ed and submitted through `efi_capsule_update()`. Errors free buffered pages and set `NO_FURTHER_WRITE_ACTION` so later writes fail until close.

State and persistence behavior: incomplete uploads own allocated pages until close or error. Successfully submitted pages are intentionally not freed because persistent capsules may need to survive until reboot. Device registration persists while the module is loaded.

Dependencies and integration points: depends on EFI runtime services, capsule support in `capsule.c`, miscdevice, highmem mapping, user-copy APIs, and platform-specific weak overrides such as Quark capsule quirks.

Risks and test signals: accepting firmware-update data is sensitive; oversized writes, invalid headers, unsupported flags, allocation failure, and incomplete close paths must fail cleanly. Test signals include device node creation only with EFI runtime services, successful capsule upload logs, `-EIO` after failed writes until close, and firmware reset-type reporting for persistent capsules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule.c

Purpose: provides the kernel EFI capsule submission core: validation with `QueryCapsuleCapabilities()`, scatter-gather block descriptor construction, serialized `UpdateCapsule()` calls, and pending-reset state tracking.

Important APIs/types/functions: exports `efi_capsule_supported()` and `efi_capsule_update()`. Internal state is `capsule_pending`, `stop_capsules`, `efi_reset_type`, and `capsule_mutex`; helpers include `efi_capsule_pending()`, `sg_pages_num()`, `efi_capsule_update_locked()`, and reboot notifier registration.

Control flow: callers validate a capsule by GUID, flags, and size. Supported flags are restricted to persist-across-reset and populate-system-table. `efi_capsule_update()` revalidates support, allocates pages for EFI block descriptor lists, fills descriptors that reference the caller's capsule data pages, adds continuation pointers, flushes cache on ARM/ARM64, then calls `efi.update_capsule()` under `capsule_mutex`. On success it marks a capsule pending and records the reset type. A reboot notifier sets `stop_capsules` so capsule updates cannot race with reset handling.

State and persistence behavior: pending capsule state is in-memory and protected by `capsule_mutex`. Capsule data pages remain caller-owned and must not be freed after successful submission. SG-list pages are retained on success because firmware may need them; they are freed only on failed submission.

Dependencies and integration points: depends on EFI runtime function pointers, architecture cache maintenance, reboot notifier chain, and the loader/device or other kernel capsule submitters.

Risks and test signals: reset-type conflicts, reboot races, unsupported flags, firmware maximum-size limits, and SG-list page lifetime are the main hazards. Test signals include `efi_capsule_supported()` returning expected errors, `efi_capsule_pending()` reporting reset type after update, and reboot paths observing pending capsules without racing new submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-arm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-arm.c

Purpose: decodes and prints ARM processor sections in UEFI Common Platform Error Records for APEI/GHES/RAS diagnostics.

Important APIs/types/functions: exports `cper_print_proc_arm()`. Internal string tables describe ARM register contexts, transaction types, cache/TLB/bus operations, bus participation, and address spaces. `cper_print_arm_err_info()` decodes validation-bit-controlled ARM error-info fields.

Control flow: `cper_print_proc_arm()` prints MIDR and optional MPIDR, affinity, and running state fields, validates that `section_length` fits within the CPER payload, then iterates error-info structures and context-info structures. Error types are converted through `cper_bits_to_str()` and further decoded for cache, TLB, and bus records. Context register payloads are hex-dumped after type and length validation; any remaining bytes are treated as vendor-specific data.

State and persistence behavior: no persistent state; output goes to kernel logs.

Dependencies and integration points: called from `cper.c` when a CPER section GUID matches `CPER_SEC_PROC_ARM` and ARM/ARM64 support is enabled. Depends on CPER structures, printk, hex dump, and shared CPER error-type strings.

Risks and test signals: malformed firmware records can claim impossible section lengths or invalid context types; the code detects these and stops decoding. Test signals are readable GHES/BERT logs for ARM processor records, graceful handling of short sections, and correct bus/cache/TLB field decoding under synthetic CPER records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-x86.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-x86.c

Purpose: decodes IA32/x64 processor sections in UEFI CPER records, including cache, TLB, bus, micro-architectural checks, CPUID data, local APIC IDs, and register context arrays.

Important APIs/types/functions: exports `cper_print_proc_ia()`. Helpers include `cper_get_err_type()`, `print_err_info()`, `print_err_info_ms()`, and `print_bool()`. Local GUIDs identify IA error structure types and macros extract validation, operation, level, overflow, and context counts.

Control flow: `cper_print_proc_ia()` prints validated LAPIC and CPUID fields, iterates the number of error-info structures encoded in validation bits, maps each error-info GUID to a known error type, prints check-info details when valid, and outputs target/requestor/responder/IP identifiers. It then iterates context structures, prints context type and array size, handles MSR/MMIO-specific addresses, delegates MSR machine-check records to `arch_apei_report_x86_error()` when possible, and hex-dumps remaining register arrays.

State and persistence behavior: no retained state; this is a log formatter.

Dependencies and integration points: used by `cper.c` under `CONFIG_UEFI_CPER_X86` for `CPER_SEC_PROC_IA` sections. Integrates with APEI x86 machine-check reporting and shared CPER processor error strings.

Risks and test signals: record sizes are trusted more than in the ARM decoder, so malformed context counts can affect traversal. Unknown GUIDs fall back to GUID printing. Test signals include correct logs from GHES IA processor errors, MSR context handoff to x86 APEI, and graceful output for unknown error/context types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper.c

Purpose: implements common UEFI CPER utilities for record IDs, severity strings, bit-string conversion, memory/PCIe/firmware/CXL/processor section printing, and generic error-status validation.

Important APIs/types/functions: exports `cper_next_record_id()`, `cper_severity_str()`, `cper_bits_to_str()`, `cper_mem_err_type_str()`, `cper_mem_err_status_str()`, `cper_mem_err_location()`, `cper_dimm_err_location()`, `cper_mem_err_pack()`, `cper_estatus_print()`, `cper_estatus_check_header()`, and `cper_estatus_check()`. Important internals are `cper_print_proc_generic()`, `cper_print_mem()`, `cper_print_pcie()`, `cper_print_fw_err()`, `cper_print_tstamp()`, and `cper_estatus_print_section()`.

Control flow: CPER consumers call `cper_estatus_check()` to validate header/raw-data offsets and section record sizes, then `cper_estatus_print()` to log severity and walk each APEI generic data section. Section dispatch is by GUID: generic processor, memory, PCIe, ARM processor, IA processor, firmware record reference, CXL protocol error, ignored CXL event records, or unknown payload hex dump. Memory sections are compacted for trace/log reuse and enriched with DMI DIMM names when possible.

State and persistence behavior: record IDs use a static atomic64 seeded from real time so ERST records stay unique across boot epochs. Otherwise the file is stateless formatting and validation code.

Dependencies and integration points: integrates ACPI APEI/GHES, DMI memory-device data, PCIe AER structures, CXL event definitions, RAS trace support, and architecture CPER processor decoders.

Risks and test signals: firmware CPER payloads are untrusted; validation gaps can lead to misleading logs or unsafe traversal. Test signals include synthetic CPER validation failures, corrected/fatal GHES log formatting, DIMM location enrichment, PCIe AER field printing, and unique ERST record IDs after reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper_cxl.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper_cxl.c

Purpose: prints CXL protocol error sections embedded in CPER records, translating agent type, agent address, device ID, serial number, capability, DVSEC, and RAS error-log fields into kernel diagnostics.

Important APIs/types/functions: exports `cxl_cper_print_prot_err()`. It uses `struct cxl_cper_sec_prot_err`, `struct cxl_ras_capability_regs`, valid-bit flags, and agent-type constants from CXL event headers.

Control flow: the printer checks each valid-bit flag before output. Address formatting depends on agent type: most CXL device/port agents use segment:bus:device.function, while RCH downstream ports use RCRB base address. Device identity, serial, capability, DVSEC, and error-log payloads are printed only for agent types where the UEFI definition makes those fields meaningful.

State and persistence behavior: no persistent state; emits diagnostic logs.

Dependencies and integration points: called by `cper.c` for `CPER_SEC_CXL_PROT_ERR` sections. Depends on CXL event ABI structures and CPER PCIe slot encoding.

Risks and test signals: variable-length DVSEC/error-log data follows the fixed structure, so malformed lengths can shift parsing. Test signals include CPER CXL protocol records with each agent class, correct RAS register printing, and no output for invalid agent/type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/cper_cxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/dev-path-parser.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/dev-path-parser.c

Purpose: maps EFI Device Path nodes to Linux `struct device` instances, currently supporting ACPI root nodes, PCI child nodes, and end-of-path markers.

Important APIs/types/functions: exports init-only `efi_get_device_by_path()`. Internal parsers are `parse_acpi_path()`, `parse_pci_path()`, `parse_end_path()`, and `match_pci_dev()`.

Control flow: `efi_get_device_by_path()` walks nodes while bytes remain. ACPI nodes validate length, derive an ACPI HID from EISA encoding, match UID, and return the first physical Linux device or the ACPI device itself. PCI nodes validate length and parent presence, then find a child PCI device by devfn. End nodes validate length/subtype, return the current parent, and either terminate the entire path or one instance. On each step the previous parent reference is dropped and the returned child becomes the new parent.

State and persistence behavior: no persistent state; returned devices have incremented references that callers must drop.

Dependencies and integration points: used by Apple property import and any EFI property/table consumer needing to bind firmware paths to Linux devices. Requires ACPI and PCI devices to exist, so callers should run no earlier than fs initcall level.

Risks and test signals: only a subset of EFI Device Path node types is implemented; unsupported paths return `-ENOTSUPP`. Pointer/length accounting must remain correct when updating `node` and `len`. Test signals include Apple property device matches on ACPI+PCI paths, correct reference balancing, and precise error offsets for malformed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/dev-path-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/earlycon.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/earlycon.c

Purpose: provides `earlycon=efifb`, a framebuffer-backed EFI early console that renders text directly into a 32-bpp EFI framebuffer before the normal console stack is ready.

Important APIs/types/functions: registers `EARLYCON_DECLARE(efifb, efi_earlycon_setup)`. Helpers include `efi_earlycon_remap_fb()`, `efi_earlycon_unmap_fb()`, `efi_earlycon_map()`, `efi_earlycon_clear_scanline()`, `efi_earlycon_scroll_up()`, `efi_earlycon_write_char()`, `efi_earlycon_write()`, and `efi_earlycon_reprobe()`.

Control flow: setup validates EFI video type and 32-bpp depth, computes the framebuffer base including high bits, chooses writeback mapping for the `ram` option or write-combine otherwise, selects a default font, scrolls the boot text area, and installs the console write callback. Before early ioremap disappears, an early initcall remaps the full framebuffer with `memremap()` if the boot console is still registered; a late initcall unmaps it unless `keep_bootcon` kept it active.

State and persistence behavior: global cursor position, font, framebuffer mapping, line-width cache, framebuffer base, and mapping mode track console state. The mapping persists through boot-console lifetime.

Dependencies and integration points: depends on `sysfb_primary_display`, font library, early_ioremap/memremap, console registration, and EFI stub/platform display table setup.

Risks and test signals: only 32-bpp framebuffers are supported, and incorrect line-length/base/size data can corrupt memory. Scrolling uses cached maximum x widths to reduce copying. Test signals include visible early boot text with `earlycon=efifb`, correct behavior with `keep_bootcon`, and no setup on non-EFI or non-32-bpp displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/earlycon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-bgrt.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-bgrt.c

Purpose: validates the ACPI Boot Graphics Resource Table image pointer, records the BGRT metadata, and reserves the firmware boot-logo BMP so later ACPI/sysfs BGRT consumers can expose it safely.

Important APIs/types/functions: global outputs are `struct acpi_table_bgrt bgrt_tab` and `size_t bgrt_image_size`. Main function is `efi_bgrt_init()`, with private `struct bmp_header`.

Control flow: `efi_bgrt_init()` exits if ACPI is disabled or EFI memory information is unavailable. It validates table length, accepts version 0 or 1 for compatibility, requires BMP image type 0 and a nonzero image address, checks the image address EFI memory type, maps the BMP header, checks magic `BM`, records image size, and reserves the image with `efi_mem_reserve()`. Any validation failure zeroes `bgrt_tab`.

State and persistence behavior: retained globals hold the validated BGRT table and image size. The image memory is reserved from general allocation.

Dependencies and integration points: called from ACPI/EFI BGRT discovery paths and depends on EFI memory type lookup, early memremap, ACPI table structures, and EFI memory reservation.

Risks and test signals: firmware may report invalid addresses, bad image types, or wrong memory types. Test signals include BGRT sysfs consumers seeing a nonzero image, logs for ignored invalid BGRT tables, and reserved boot-logo memory not being reused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-bgrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-init.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-init.c

Purpose: initializes EFI on FDT-based architectures by reading EFI boot parameters from the device tree, mapping the EFI memory map and system table, parsing config tables, populating memblock from EFI memory descriptors, and setting up display/table side effects.

Important APIs/types/functions: exports/defines `primary_display_table`, `sysfb_primary_display` on non-x86, and `efi_init()`. Helpers include `is_memory()`, `efi_to_phys()`, `init_primary_display()`, `uefi_init()`, `is_usable_memory()`, and `reserve_regions()`.

Control flow: `efi_init()` obtains system-table and memmap parameters via `efi_get_fdt_params()`, initializes the early EFI memmap, validates descriptor version, maps and checks the system table, records runtime pointer/version, reports firmware header, parses config tables, and then rebuilds memblock from EFI memory descriptors. Usable writeback memory is added as RAM; non-usable memory is nomapped; ACPI reclaim memory is reserved; special-purpose memory can be skipped for soft reservation. It then caps usable ranges, finds mirrored memory, initializes ESRT and MOK variable tables, reserves the memmap, and initializes primary display data when relevant.

State and persistence behavior: sets `efi.flags`, `efi.runtime`, config table globals, memblock memory/reservation state, primary display state, and reserved EFI memmap storage.

Dependencies and integration points: depends on FDT parameters, EFI memmap/config parser, memblock, OF memory helpers, KHO scratch preservation, sysfb/earlycon, ESRT, MOK variables, and architecture EFI support.

Risks and test signals: if the EFI memory map cannot be mapped, boot panics because no other reliable memory description exists. Incorrect memblock rebuilding can hide RAM or expose reserved regions. Test signals include EFI boot logs, correct `/proc/iomem` RAM/reserved layout, sysfb early console reprobe, ESRT availability, and successful FDT EFI boot on ARM/RISC-V-like platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-pstore.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-pstore.c

Purpose: registers EFI variables as a pstore backend for crash/dmesg records, storing and enumerating records under the `LINUX_EFI_CRASH_GUID` namespace.

Important APIs/types/functions: main pstore callbacks are `efi_pstore_open()`, `efi_pstore_close()`, `efi_pstore_read()`, `efi_pstore_write()`, and `efi_pstore_erase()`. Helpers include `efi_pstore_read_func()`, `generic_id()`, `efivars_pstore_init()`, `efivars_pstore_exit()`, and the runtime `pstore_disable` parameter setter.

Control flow: module init checks EFI variable write support and the disable flag, clamps `record_size` to at least 1024, allocates the pstore buffer, and calls `pstore_register()`. Reads lock efivars, enumerate variables with `efivar_get_next_variable()`, filter by crash GUID, parse legacy and current `dump-type...` names, read variable data, and store a UCS-2 name copy for later erase. Writes format a UCS-2 variable name with type/part/count/time/compression, try-lock efivars, and set a nonvolatile runtime variable. Erase sets the variable size to zero.

State and persistence behavior: crash records persist in EFI nonvolatile variable storage across reboot until erased. Runtime state includes the pstore buffer, enumeration name buffer in `psi->data`, and module parameters.

Dependencies and integration points: depends on the EFIVAR namespace API, pstore core, UCS-2 conversion, EFI variable runtime services, and firmware variable-store capacity/quirks.

Risks and test signals: EFI variable stores are small and firmware-specific; write failures, enumeration size quirks, lock contention, and excessive record fragmentation are important risks. Test signals include pstore registration, crash records under pstore after reboot, successful erase, `pstore_disable` toggling registration, and sane behavior when writes are unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-pstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi.c

Purpose: implements the generic EFI subsystem: global EFI state, command-line options, `/sys/firmware/efi`, efivar backend registration, config-table parsing, memory-map helpers, EFI memory reservation, random seed handling, runtime workqueue setup, and selected kexec/reboot integration.

Important APIs/types/functions: exports global `struct efi efi`, `efivar_ops_nh`, `efivars_generic_ops_register()`, `efivars_generic_ops_unregister()`, `efi_mem_desc_lookup()`, `efi_status_to_err()`, and many init helpers. Important functions include `parse_efi_cmdline()`, `efisubsys_init()`, `efi_find_mirror()`, `__efi_mem_desc_lookup()`, `efi_mem_reserve()`, `efi_config_parse_tables()`, `efi_systab_check_header()`, `efi_systab_report_header()`, `efi_md_typeattr_format()`, `efi_mem_attributes()`, `efi_mem_type()`, `efi_mem_reserve_persistent()`, and kexec random-seed update hooks.

Control flow: early params set debug/runtime/soft-reserve flags. `efi_config_parse_tables()` walks firmware config tables, records known GUID addresses, seeds kernel randomness from EFI RNG data, initializes memory attributes/TPM logs, reserves EFI memreserve entries, applies runtime-properties masks, imports initrd metadata, and reserves unaccepted-memory tables. `subsys_initcall(efisubsys_init)` creates an ordered EFI runtime workqueue when needed, registers EFI RTC and efivar platform devices, creates `/sys/firmware/efi` attributes and `efivars` mount point, registers generic efivar ops, optionally loads SSDT overlays from efivars, initializes debugfs boot-service blobs, and probes optional OVMF/Coco devices.

State and persistence behavior: `efi` stores config table addresses and runtime support flags for kernel lifetime. `efi_mm`, `efi_rts_wq`, `efi_kobj`, memreserve root mappings, persistent memreserve linked-list entries, and sysfs/debugfs objects persist after init. Persistent reservations can be appended for kexec handoff.

Dependencies and integration points: central integration point for EFI runtime wrappers, efivars, ACPI, TPM, initrd, memblock, random subsystem, kexec, sysfs/debugfs, platform devices, and architecture config-table extensions.

Risks and test signals: config-table addresses and memory descriptors are firmware-controlled; usability checks, x86-32 high-address rejection, memreserve traversal, and runtime support masks prevent unsafe access. Test signals include `/sys/firmware/efi/{systab,fw_platform_size,efivars}`, efivarfs mountability, EFI RNG seed consumption, TPM log detection, persistent memreserve behavior across kexec, and correct error conversion for runtime service failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efibc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/efibc.c

Purpose: implements EFI Bootloader Control by writing bootloader variables during reboot so compatible bootloaders can perform a one-shot boot entry selection and know the reboot reason.

Important APIs/types/functions: key functions are `efibc_set_variable()`, `efibc_reboot_notifier_call()`, `efibc_init()`, and `efibc_exit()`. It registers `efibc_reboot_notifier`.

Control flow: module init requires EFI `SetVariable` runtime support, then registers a reboot notifier. On reboot/shutdown, the notifier writes `LoaderEntryRebootReason` as `reboot` or `shutdown`. If reboot command data is present, it copies up to 511 bytes into UCS-2 and writes `LoaderEntryOneShot`.

State and persistence behavior: state is stored in nonvolatile EFI variables under `LINUX_EFI_LOADER_ENTRY_GUID`, so it survives until consumed/cleared by the bootloader.

Dependencies and integration points: depends on EFI runtime `set_variable`, reboot notifier chain, UCS-2 strings, and bootloaders honoring the LoaderEntry variables.

Risks and test signals: runtime variable writes can fail due to firmware policy, full variable store, or missing runtime services. Test signals include variables appearing before reset, bootloader performing the one-shot entry, and clean notifier unregister on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/efibc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/embedded-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/embedded-firmware.c

Purpose: scans EFI boot-services code regions for known embedded peripheral firmware blobs on DMI-matched systems and makes matched blobs available to drivers.

Important APIs/types/functions: exports test namespace symbols `efi_embedded_fw_list` and `efi_embedded_fw_checked`, and exports `efi_get_embedded_fw()`. Main helpers are `efi_check_for_embedded_firmwares()` and `efi_check_md_for_embedded_firmware()`.

Control flow: `efi_check_for_embedded_firmwares()` iterates DMI tables such as `touchscreen_dmi_table`, skips empty descriptors, then scans each EFI memory descriptor of type `EFI_BOOT_SERVICES_CODE`. Each descriptor is memremapped, searched at 8-byte offsets for the descriptor prefix, verified by SHA-256 over the expected blob length, duplicated into kernel memory, and linked into `efi_embedded_fw_list`. Lookup later requires the scan-complete flag and returns data/size by firmware name.

State and persistence behavior: matched firmware blobs are copied into heap memory and retained in a global list for driver requests. The checked flag records that scanning has completed.

Dependencies and integration points: depends on DMI matching, EFI memory map descriptors, crypto SHA-256, memremap, and firmware consumers using `efi_get_embedded_fw()`.

Risks and test signals: assumptions are explicit: blobs are in boot-services code and aligned to 8 bytes. False positives are mitigated by prefix plus SHA-256. Test signals include DMI-matched hardware finding the expected blob, test firmware namespace checks, and `-ENOENT` before scan completion or for unknown names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/embedded-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/esrt.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/esrt.c

Purpose: validates and reserves the EFI System Resource Table during early boot, then exposes firmware-update resource entries under `/sys/firmware/efi/esrt`.

Important APIs/types/functions: defines ESRT wire structs `efi_system_resource_table` and `efi_system_resource_entry_v1`, runtime `struct esre_entry`, top-level and per-entry sysfs attributes, `efi_esrt_init()`, `esrt_sysfs_init()`, `register_entries()`, and `esre_create_sysfs_entry()`.

Control flow: `efi_esrt_init()` requires EFI memory/config-table support, verifies the ESRT address is in an acceptable EFI memory descriptor, checks header fit, version 1, entry size capacity, a conservative count limit of 128, and full table fit in one memory-map entry. It records physical address/size and reserves boot-services data with `efi_mem_reserve()`. `device_initcall(esrt_sysfs_init)` maps the reserved table, creates the `esrt` kobject and `entries` kset, publishes top-level count/version attributes, and creates `entryN` kobjects for each resource.

State and persistence behavior: early physical address/size survive until sysfs init; the table is memremapped for sysfs reads. Per-entry kobjects remain until shutdown.

Dependencies and integration points: depends on EFI config table parsing, EFI memory descriptor lookup, memblock reservation, sysfs/kobject APIs, and userspace firmware update tools such as fwupd.

Risks and test signals: ESRT is firmware-provided and must fit in a single descriptor; bad counts or unsupported versions are rejected. Test signals include `/sys/firmware/efi/esrt/fw_resource_count`, `entries/entry*/fw_class`, correct reservation logs, and graceful `-ENOSYS` when no ESRT exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/esrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/fdtparams.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/fdtparams.c

Purpose: extracts EFI system-table and memory-map parameters from the flattened device tree for architectures that receive EFI boot metadata through `/chosen` or Xen's `/hypervisor/uefi` node.

Important APIs/types/functions: exports init-only `efi_get_fdt_params()`. Helper `efi_get_fdt_prop()` reads 32-bit or 64-bit big-endian properties into target variables and logs values under `efi=debug`.

Control flow: `efi_get_fdt_params()` checks `initial_boot_params`, then searches known nodes in priority order. For each found node it reads system table, memmap base, memmap size, descriptor size, and descriptor version properties. Missing system-table property falls through to the next node; missing later properties abort EFI discovery. Xen/paravirt nodes set `EFI_PARAVIRT`.

State and persistence behavior: fills the caller's `struct efi_memory_map_data` and returns the EFI system-table address. It may set an EFI flag; no additional state is retained.

Dependencies and integration points: used by `efi_init()` on FDT-based EFI boots. Depends on libfdt, initial boot params, unaligned big-endian reads, and optional Xen property names.

Risks and test signals: incorrect DT property sizes or absent required properties disable EFI init. 64-bit values are saturated when stored into 32-bit descriptor-size/version fields. Test signals include `efi=debug` property logs, successful EFI boot through `/chosen`, and `EFI_PARAVIRT` set for Xen-provided UEFI parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/fdtparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/Makefile

Purpose: builds the EFI boot stub as freestanding, relocation-safe code for multiple architectures, with special compiler flags, object-copy rewriting, architecture object selection, and zboot support.

Important APIs/types/functions: assembles `lib-y` from generic stub helpers, architecture stubs, string/intrinsics, libfdt objects, zboot decompressors, unaccepted-memory helpers, and selected support code. It defines `KBUILD_CFLAGS`, architecture cflags, `STUBCOPY_FLAGS-*`, `STUBCOPY_RELOC-*`, and the `%.stub.o` objcopy verification rule.

Control flow: no runtime flow. Build flow removes tracing, stack protector, fortify, struct randomization, SCS, CFI, and LTO from stub builds, compiles objects as PIC/PIE as needed, imports selected `lib/` C files, prefixes/renames sections for ARM/ARM64/RISC-V/LoongArch, and checks for forbidden absolute relocations before producing `.stub.o` objects.

State and persistence behavior: build artifacts only.

Dependencies and integration points: tightly coupled to architecture image formats, EFI stub C code, libfdt, zlib/zstd decompression, binutils `objcopy`/`objdump`, and kernel linker scripts.

Risks and test signals: EFI stub code runs before normal kernel runtime support, so accidental instrumentation, absolute relocations, or wrong section flags can break boot. Test signals include successful PE/COFF boot images for each architecture, relocation check failures when absolute references appear, and zboot decompression builds for enabled algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/alignedmem.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/alignedmem.c

Purpose: provides aligned EFI page allocation for the boot stub, returning an allocation base that satisfies architecture alignment while staying below a maximum address.

Important APIs/types/functions: defines `efi_allocate_pages_aligned(size, addr, max, align, memory_type)`.

Control flow: the allocator clamps `max` to `EFI_ALLOC_LIMIT`, raises `align` to at least `EFI_ALLOC_ALIGN`, rounds `size`, requests extra slack pages with `EFI_ALLOCATE_MAX_ADDRESS`, aligns the returned address upward, and frees unused leading/trailing slack pages around the aligned usable region.

State and persistence behavior: no file-local state; allocated EFI pages persist until the caller frees them or boot services exit.

Dependencies and integration points: used by EFI stub image allocation paths and depends on `efi_bs_call(allocate_pages/free_pages)`, EFI page sizing, and architecture alignment constants.

Risks and test signals: slack calculations must not free pages inside the aligned result or leak pages outside it. Test signals include aligned kernel/initrd allocations under varied firmware allocation bases and successful boot with large alignment requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/alignedmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm32-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm32-stub.c

Purpose: implements ARM 32-bit EFI stub platform checks, CPU-entry-state handoff, post-ExitBootServices state capture, and decompressed kernel placement.

Important APIs/types/functions: defines global `efi_entry_state`, `check_platform_features()`, `efi_handle_post_ebs_state()`, `handle_kernel_image()`, and private `get_cpu_state()`.

Control flow: `check_platform_features()` reads CPSR/SCTLR, logs HYP/SVC and MMU state, allocates an `efi_arm_entry_state`, installs it as a Linux EFI config table, and rejects LPAE kernels on CPUs without sufficient memory-model support. `efi_handle_post_ebs_state()` records CPSR/SCTLR after ExitBootServices. `handle_kernel_image()` allocates a low decompression area, computes a 16 MiB-aligned kernel base allowing `TEXT_OFFSET` slack, frees unused pages, and returns image/reserve addresses for the common stub.

State and persistence behavior: CPU entry-state data is allocated from EFI loader data and passed through a config table to the kernel. Reserved decompression memory persists through stub handoff.

Dependencies and integration points: depends on ARM system registers, EFI boot services, `TEXT_OFFSET`, `MAX_UNCOMP_KERNEL_SIZE`, `EFI_PHYS_ALIGN`, and common stub allocation/free flow.

Risks and test signals: wrong alignment or slack handling can place the decompressed kernel where firmware still owns memory. LPAE feature detection must reject incompatible CPUs. Test signals include boot logs with entry mode/MMU state, visible CPU state table in kernel, and successful ARM EFI boot across alignment edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm32-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64-stub.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64-stub.c

Purpose: handles arm64 kernel image validation, KASLR relocation, entry offset calculation for in-kernel stubs, and instruction-cache synchronization.

Important APIs/types/functions: defines `handle_kernel_image()`, `primary_entry_offset()`, and `efi_icache_sync()`.

Control flow: `handle_kernel_image()` corrects bogus firmware `image_base`, warns on segment misalignment, calculates kernel file/code/memory sizes from linker symbols, seeds KASLR from the EFI handle, and delegates relocation to `efi_kaslr_relocate_kernel()`. `primary_entry_offset()` returns the true `primary_entry` offset because the PE/COFF header may not be present in the in-memory kernel image. `efi_icache_sync()` cleans/invalidates caches to point of unification.

State and persistence behavior: no persistent state; relocation outputs reserve/image addresses for common stub handling.

Dependencies and integration points: depends on arm64 linker symbols, KASLR stub helpers, cache maintenance, EFI loaded image protocol, and common stub entry flow.

Risks and test signals: incorrect image-base handling, segment alignment, or code/memory size calculation can break relocation or execution permissions. Test signals include KASLR-enabled EFI boot, warning on bad firmware image base without boot failure, and correct branch into `primary_entry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64.c

Purpose: implements arm64 EFI stub platform feature checks, virtual-address-map workaround selection, cache synchronization/remapping, and final kernel entry.

Important APIs/types/functions: key functions are `check_platform_features()`, `efi_cache_sync_image()`, weak `primary_entry_offset()`, and `efi_enter_kernel()`. Helper `system_needs_vamap()` identifies Ampere systems needing `SetVirtualAddressMap()`.

Control flow: feature checks set `efi_novamap` when 48-bit TTBR0 mappings allow 1:1 runtime access and the system is not an Ampere eMAG/Altra workaround case. Non-4K page kernels verify CPU translation granule support. Cache sync cleans data cache lines for code when IDC is absent, invalidates instruction cache, executes barriers, then calls `efi_remap_image()`. Final entry adds `primary_entry_offset()` to the entry point and calls the kernel with FDT address and zeroed registers.

State and persistence behavior: may set global stub state `efi_novamap`; otherwise stateless.

Dependencies and integration points: depends on ARM64 CPU feature registers, SMBIOS records/strings, EFI remap helpers, cache maintenance instructions, and common stub entry.

Risks and test signals: wrong granule detection can boot unsupported kernels; skipping virtual address map on affected Ampere systems breaks runtime `SetTime()`. Test signals include 16K/64K page rejection on unsupported CPUs, Ampere workaround log, and successful kernel entry after cache sync/remap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/bitmap.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/bitmap.c

Purpose: supplies minimal bitmap set/clear primitives for EFI stub code that cannot rely on the full kernel bitmap implementation.

Important APIs/types/functions: defines `__bitmap_set()` and `__bitmap_clear()`.

Control flow: both helpers compute the starting word, first-word mask, and total end bit, then iterate whole words applying set or clear masks. The final partial word is masked with `BITMAP_LAST_WORD_MASK()`.

State and persistence behavior: no internal state; mutates caller-provided bitmaps.

Dependencies and integration points: used by EFI stub unaccepted-memory helpers and depends only on lightweight bitmap macros available in the freestanding stub build.

Risks and test signals: off-by-one errors would mark wrong physical ranges accepted/unaccepted. Test signals include bitmap operations crossing word boundaries, zero/partial lengths, and unaccepted-memory boot tests using the stub bitmap implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-entry.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-entry.c

Purpose: provides the generic EFI PE/COFF entry point used by ARM, arm64, RISC-V, and LoongArch stubs, bridging firmware invocation to common stub setup and kernel handoff.

Important APIs/types/functions: defines `efi_pe_entry()`, `alloc_primary_display()`, private `kernel_image_addr()`, and `kernel_image_offset`.

Control flow: `efi_pe_entry()` stores the EFI system table, validates its signature, obtains the loaded image protocol, parses the EFI command line, logs boot start, calls architecture `handle_kernel_image()` to relocate or reserve the kernel image, records the image offset for in-image data references, invokes `efi_stub_common()`, and frees temporary image/reserve allocations before returning firmware status. `alloc_primary_display()` returns architecture-appropriate storage for primary display data.

State and persistence behavior: `kernel_image_offset` records relocation delta while the stub runs. Other persistent handoff state is managed by common stub code and architecture handlers.

Dependencies and integration points: depends on EFI loaded image protocol, architecture `handle_kernel_image()`, common command-line and stub setup helpers, sysfb primary display storage, and EFI boot services.

Risks and test signals: failures before `efi_stub_common()` must return EFI status without leaking allocations; freeing image/reserve ranges must match architecture allocation semantics. Test signals include valid PE entry on supported architectures, command-line parsing, correct primary display handoff, and clean return codes on missing loaded-image protocol or relocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/efi-stub-entry.c -->
