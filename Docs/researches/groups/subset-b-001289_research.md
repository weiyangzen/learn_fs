# subset-b-001289 Research

Grouped research for the firmware subset. Each source file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/mm_communication.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/mm_communication.h

Purpose: Defines the wire-format contract between Linux EFI variable code and StandaloneMM (StMM) running inside OP-TEE. It is a protocol header, not executable code, and keeps Linux-side struct layouts aligned with EDK2/PI concepts such as EFI_MM_COMMUNICATE_HEADER and SMM variable command payloads.

Important APIs/types/functions: The main types are `efi_mm_communicate_header`, `smm_variable_communicate_header`, `smm_variable_access`, `smm_variable_payload_size`, `smm_variable_getnext`, `smm_variable_query_info`, `var_check_property`, and `smm_variable_var_check_property`. Constants identify the OP-TEE pseudo-TA (`PTA_STMM_UUID`), the EFI MM variable GUID, the PTA command (`PTA_STMM_CMD_COMMUNICATE`), SPM return codes, and StMM variable function IDs for get/set/query/enumerate/property/payload calls.

Control flow: No runtime flow is implemented here. Consumers allocate a communication buffer beginning with `efi_mm_communicate_header`, place a `smm_variable_communicate_header` in `data`, then append the function-specific payload type described by the `SMM_VARIABLE_FUNCTION_*` selector.

State and persistence behavior: The header describes persistent EFI variables and variable property metadata but stores no state itself. Fields such as name/data sizes and variable attributes are passed through to secure firmware, where persistent storage decisions are made.

Dependencies and integration points: Depends on kernel EFI GUID/status types, `BIT()`, and packed/flexible-array conventions. It is directly included by `tee_stmm_efi.c`, which relies on exact field sizes for shared-memory communication with OP-TEE and StandaloneMM.

Risks and test signals: Layout drift, size_t width assumptions, or GUID endian confusion would break the secure-firmware ABI. Useful tests are compile coverage across supported architectures, EFI variable get/set/enumeration tests through the TEE backend, and negative tests for oversized payloads and read-only property handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/mm_communication.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/tee_stmm_efi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/tee_stmm_efi.c

Purpose: Provides an EFI variable backend that routes variable runtime services through OP-TEE to StandaloneMM. On probe it replaces the generic EFI variable operations with TEE-backed operations and restores the generic backend on removal.

Important APIs/types/functions: `tee_stmm_efi_private` stores the TEE context, session, and device. `tee_mm_communicate()` registers a kernel buffer as TEE shared memory and invokes `PTA_STMM_CMD_COMMUNICATE`. `setup_mm_hdr()` allocates and fills the MM/SMM headers. `get_max_payload()` discovers StMM payload limits. Runtime service callbacks are `tee_get_variable()`, `tee_get_next_variable()`, `tee_set_variable()`, `tee_set_variable_nonblocking()`, and `tee_query_variable_info()`.

Control flow: Probe opens an OP-TEE context matching `TEE_IMPL_ID_OPTEE`, opens a PTA session using the StMM UUID, queries maximum payload size, unregisters generic efivars, and registers `tee_efivar_ops`. Each variable call builds a packed communication buffer, sends it through `tee_client_invoke_func()`, maps SPM errors to EFI statuses, reads `ret_status`, then copies returned data back into kernel buffers.

State and persistence behavior: Global `pvt_data`, `max_payload_size`, `max_buffer_size`, and `tee_efivars` represent process-wide backend state. Persistent variable state lives in StMM firmware. The driver enforces StMM read-only variable properties before set operations.

Dependencies and integration points: Integrates the TEE client bus, OP-TEE PTA ABI, `efivars_register()`, `efivars_generic_ops_unregister()`, UCS-2 helpers, and allocation via `alloc_pages_exact()`. It consumes the protocol definitions in `mm_communication.h`.

Risks and test signals: Key risks are shared-memory registration failures, firmware payload limit mismatches, truncated variable buffers, races around global backend replacement, and property handling that converts `EFI_NOT_FOUND` to writable state. Tests should exercise get/set/delete/enumerate/query through `/sys/firmware/efi/efivars` and `efi_test`, including oversized names/data, null data pointers, read-only variables, and module unload/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/tee_stmm_efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/sysfb_efi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/sysfb_efi.c

Purpose: Applies EFI framebuffer quirks and firmware-node links for generic system framebuffer registration. It compensates for broken EFI framebuffer descriptors on known systems, especially older Apple hardware and portrait-panel devices.

Important APIs/types/functions: `efifb_dmi_list` stores per-model fallback base, stride, width, height, and override flags. `efifb_setup_from_dmi()` supports boot option lookup. `efifb_set_system()` applies DMI data and validates hard-coded framebuffer bases against VGA PCI BARs. `sysfb_apply_efi_quirks()` drives DMI matching, and `sysfb_set_efifb_fwnode()` attaches a fwnode that can add DT PCI dependency links.

Control flow: During sysfb setup, quirks are skipped or applied based on `orig_video_isVGA` and `VIDEO_CAPABILITY_SKIP_QUIRKS`. DMI callbacks either fill missing framebuffer fields or swap width/height for portrait devices. In DT mode, fwnode `add_links` scans PCI host ranges and links efifb to the PCI controller that owns the memory window.

State and persistence behavior: Mutates the global primary `screen_info` fields for framebuffer base, dimensions, stride, size, and video type. No persistent storage is written; the state affects later platform-device registration and framebuffer driver binding.

Dependencies and integration points: Uses DMI, EFI screen info, PCI resource APIs, OF PCI range parsing, sysfb, and VGA video constants. Downstream consumers include simplefb, corebootdrm/DRM, efifb, and sysfb platform-device creation.

Risks and test signals: Incorrect DMI matches can corrupt display geometry; wrong base validation can suppress a valid boot console; DT fwnode links can affect probe order. Test signals include booting listed systems, verifying `/proc/iomem` reservations and framebuffer dimensions, checking portrait device rotation fixups, and ensuring PCI-backed framebuffers do not conflict with host bridge windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/sysfb_efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/Makefile

Purpose: Builds the EFI runtime service test misc driver when `CONFIG_EFI_TEST` is enabled.

Important APIs/types/functions: The only build rule is `obj-$(CONFIG_EFI_TEST) += efi_test.o`, binding the Kconfig option to `efi_test.c`.

Control flow: No runtime control flow. Kbuild includes the object in built-in or module output according to the tristate value selected by configuration.

State and persistence behavior: No state. It determines whether the `/dev/efi_test` interface code is present in the kernel/module build.

Dependencies and integration points: Integrates with the EFI firmware driver subtree and Kbuild. It assumes the source file exports a normal module init/exit pair.

Risks and test signals: Risk is limited to build coverage; a stale object name or missing Kconfig symbol would silently omit the test driver. Test by enabling `CONFIG_EFI_TEST=m/y`, building, and confirming `efi_test.ko` or built-in registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.c

Purpose: Exposes selected EFI runtime services to privileged userspace through a misc device named `efi_test`. It is a diagnostic/testing bridge for firmware operations such as variable access, time services, wake alarm, monotonic count, capsule capability query, reset, and runtime support mask reporting.

Important APIs/types/functions: Helpers copy UCS-2 strings between user and kernel memory. IOCTL handlers include `efi_runtime_get_variable()`, `efi_runtime_set_variable()`, `efi_runtime_get_time()`, `efi_runtime_set_time()`, `efi_runtime_get_waketime()`, `efi_runtime_set_waketime()`, `efi_runtime_get_nextvariablename()`, `efi_runtime_query_variableinfo()`, `efi_runtime_query_capsulecaps()`, and `efi_runtime_reset_system()`. `efi_test_ioctl()` dispatches the ioctl numbers from `efi_test.h`.

Control flow: `efi_test_init()` registers a misc device. `open` rejects use under EFI lockdown and requires `CAP_SYS_ADMIN`. Each ioctl copies a packed userspace request, marshals optional pointers and buffers, calls the matching `efi.*` runtime service, writes EFI status back to userspace, and returns Linux errors for copy or firmware failures.

State and persistence behavior: The driver itself is stateless aside from misc-device registration. It can mutate persistent EFI NVRAM through set-variable, system time/wake alarm through EFI services, and can trigger reset through `efi.reset_system()`.

Dependencies and integration points: Relies on the global EFI runtime-services table, Linux security lockdown, capability checks, miscdevice, uaccess, and the ABI structs in `efi_test.h`. It can test whichever EFI variable backend is active, including generic, GSMI, or TEE STMM.

Risks and test signals: This is intentionally powerful and must remain locked to admin and lockdown policy. User pointer validation, buffer-size reporting, and capsule pointer-array copying are high-risk paths. Test with negative uaccess cases, zero-length/oversized buffers, EFI_BUFFER_TOO_SMALL propagation, lockdown enforcement, and each ioctl against known EFI firmware or a virtualized EFI environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.h

Purpose: Defines the userspace ABI for the EFI runtime test driver. It documents the packed request structures and ioctl command numbers used by `/dev/efi_test`.

Important APIs/types/functions: ABI structures include `efi_getvariable`, `efi_setvariable`, `efi_getnextvariablename`, `efi_queryvariableinfo`, `efi_gettime`, `efi_settime`, `efi_getwakeuptime`, `efi_setwakeuptime`, `efi_getnexthighmonotoniccount`, `efi_querycapsulecapabilities`, and `efi_resetsystem`. IOCTLs use `_IOW`, `_IOR`, and `_IOWR` with command group `p` and numbers `0x01` through `0x0C`.

Control flow: No executable flow. `efi_test.c` copies these packed structures from userspace and dispatches based on the ioctl definitions.

State and persistence behavior: No state is stored here. The structs expose pointers to status fields and runtime-service inputs that can cause persistent EFI variable writes, time changes, or resets when consumed by the driver.

Dependencies and integration points: Depends on `linux/efi.h` for EFI types. Any userspace test program must match these layouts exactly, including pointer width and packed layout of the running kernel ABI.

Risks and test signals: ABI changes would break existing test tools. Packed pointer-containing structs make 32-bit compatibility and native word-size assumptions important. Test signals include ioctl compilation against this header, native userspace round trips, and compat-mode review if the driver is exposed on mixed ABI systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/tpm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/tpm.c

Purpose: Reserves EFI TPM event log memory early and calculates the TPM 2.0 final events table size so later TPM event-log consumers can safely access firmware-provided logs.

Important APIs/types/functions: `efi_tpm_final_log_size` is exported for consumers. `tpm2_calc_event_log_size()` walks a fixed number of TPM2 event records using `__calc_tpm2_event_size()`. `efi_tpm_eventlog_init()` maps the EFI TPM log table, reserves it with memblock, optionally maps/parses the final events table, reserves that memory, and records the final log size.

Control flow: If `efi.tpm_log` is absent, initialization returns success without work. Otherwise it early-maps the event log header, reserves the header plus log payload, validates final-events prerequisites, maps the final table header, calculates event payload size from the original log's algorithm info, reserves final-events memory, and unmaps temporary mappings.

State and persistence behavior: Mutates global EFI table addresses on mapping failure and writes exported `efi_tpm_final_log_size`. It reserves physical ranges in memblock but does not alter firmware logs.

Dependencies and integration points: Uses EFI configuration table addresses, early ioremap, memblock, TPM event-log parsing helpers, and TCG2 table structures. Later TPM log drivers depend on the reserved ranges staying intact.

Risks and test signals: Firmware can report malformed event sizes or unsupported formats; calculation failure returns `-EINVAL`. A notable risk is final-table `events` pointer arithmetic based on physical table address conventions. Test signals include EFI boots with TPM2 final events, malformed table injection, memblock reservation visibility, and TPM event log users seeing the expected final log length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/tpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/unaccepted_memory.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/unaccepted_memory.c

Purpose: Manages EFI unaccepted-memory bitmaps for confidential-computing guests, accepting pages on demand and reporting whether ranges still contain unaccepted memory.

Important APIs/types/functions: `accept_memory()` accepts a physical range and clears the corresponding bitmap bits. `range_contains_unaccepted_memory()` checks bitmap state. `accept_range` and `accepting_list` coordinate concurrent acceptance of overlapping unit-size ranges. Optional vmcore callback `unaccepted_memory_vmcore_pfn_is_ram()` excludes unaccepted pages from crash dump RAM.

Control flow: Calls first obtain the EFI unaccepted table and clamp the request to the bitmap-covered physical range. Both acceptance and lookup extend unit-aligned end boundaries by one unit to avoid speculative or unaligned loads into unaccepted memory. `accept_memory()` serializes overlapping ranges, iterates set bit ranges, calls `arch_accept_memory()`, clears bits, removes the active range, and touches the soft lockup watchdog.

State and persistence behavior: The persistent state is the EFI-provided bitmap, modified in place as memory becomes accepted. `accepting_list` is transient in-kernel synchronization state protected by `unaccepted_memory_lock`.

Dependencies and integration points: Depends on `efi_get_unaccepted_table()`, architecture acceptance hooks, bitmap helpers, spinlocks, crash dump vmcore callbacks, and confidential-computing platform semantics such as TDX.

Risks and test signals: Deadlock avoidance depends on interrupt-disabled locking around acceptance. Off-by-one bitmap translation can accept too little or scan outside the represented range. Test signals include concurrent acceptance stress, unit-boundary lookups, kdump filtering, and platform-specific acceptance validation under TDX/SEV-SNP-like guests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/unaccepted_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/vars.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/efi/vars.c

Purpose: Implements the common EFI variable operation registry and serialized helper API used by variable filesystems and alternate EFI backends.

Important APIs/types/functions: Global `__efivars` points to the active backend. `efivars_register()` and `efivars_unregister()` install/remove one `struct efivars`. `efivar_lock()`, `efivar_trylock()`, and `efivar_unlock()` expose serialization. Helper wrappers include `efivar_get_variable()`, `efivar_get_next_variable()`, `efivar_set_variable_locked()`, `efivar_set_variable()`, `efivar_query_variable_info()`, `efivar_is_available()`, and `efivar_supports_writes()`.

Control flow: Registration takes the semaphore, rejects a second backend, stores ops, emits notifier state for read-only/read-write capability, and logs success. Set-variable calls validate variable-store capacity via `query_variable_store` or a 64 KiB fallback, select blocking or nonblocking set ops, then call the backend under the required lock.

State and persistence behavior: Maintains one global backend pointer and semaphore. It does not store EFI variables directly, but all persistent NVRAM mutations route through backend ops. Notifier events inform other subsystems when operations become available.

Dependencies and integration points: Integrates Linux EFI type definitions, UCS-2 sizing, EFIVAR namespace exports, notifier chain `efivar_ops_nh`, and backend drivers such as generic EFI runtime services, GSMI, and TEE STMM.

Risks and test signals: Callers must hold the lock for low-level helpers; missing `__efivars` checks in some helpers assume proper availability sequencing. Backend replacement must avoid races with users. Tests should cover double registration, unregister mismatch, lock failure paths, nonblocking set behavior, variable size checks, and notifier behavior on read-only vs read-write backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/efi/vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/Kconfig

Purpose: Defines configuration switches for Google/coreboot firmware drivers: GSMI SMI services, coreboot table enumeration, CBMEM sysfs export, firmware memconsole variants, coreboot framebuffer registration, and VPD sysfs export.

Important APIs/types/functions: `GOOGLE_FIRMWARE` gates the submenu. Symbols include `GOOGLE_SMI`, `GOOGLE_CBMEM`, `GOOGLE_COREBOOT_TABLE`, `GOOGLE_MEMCONSOLE`, `GOOGLE_MEMCONSOLE_X86_LEGACY`, `GOOGLE_FRAMEBUFFER_COREBOOT`, `GOOGLE_MEMCONSOLE_COREBOOT`, and `GOOGLE_VPD`.

Control flow: No runtime flow. Kconfig dependencies select which source files are compiled and enforce platform prerequisites such as X86/ACPI/DMI for legacy SMI/EBDA paths or `HAS_IOMEM && (ACPI || OF)` for coreboot table access.

State and persistence behavior: No direct state. Build choices determine whether drivers expose sysfs firmware state, EFI variables through GSMI, or framebuffer/memconsole platform devices.

Dependencies and integration points: Coordinates dependencies among Google firmware drivers. CBMEM, VPD, memconsole-coreboot, and framebuffer-coreboot depend on the coreboot table bus; memconsole variants select the shared memconsole core.

Risks and test signals: Wrong dependencies can create link errors or unusable drivers on unsupported platforms. Test signals are allmodconfig/build coverage, module dependency checks, and boot tests on coreboot ACPI and DT systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/Makefile

Purpose: Maps Google firmware Kconfig symbols to objects and composes the VPD sysfs module from parser and sysfs pieces.

Important APIs/types/functions: Builds `gsmi.o`, `coreboot_table.o`, `framebuffer-coreboot.o`, `memconsole.o`, `memconsole-coreboot.o`, `memconsole-x86-legacy.o`, `cbmem.o`, and the composite `vpd-sysfs.o` from `vpd.o vpd_decode.o`.

Control flow: No runtime flow. Object ordering notes that `cbmem.o` must follow `coreboot_table.o` because it depends on the bus type exported by the table driver.

State and persistence behavior: No state. The file controls which modules are available for exposing firmware memory, logs, NVRAM, and VPD.

Dependencies and integration points: Integrates with Kbuild and the Kconfig symbols defined in the same directory. The composite VPD module links the decoder with the coreboot driver.

Risks and test signals: Ordering and composite-object names must remain consistent with module aliases and dependencies. Test with built-in and modular configurations for each symbol, especially `CONFIG_GOOGLE_VPD=m` and `CONFIG_GOOGLE_COREBOOT_TABLE=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/cbmem.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/cbmem.c

Purpose: Exposes coreboot CBMEM entries as sysfs devices under the coreboot bus, including physical address, size, and a binary `mem` attribute backed by the mapped memory region.

Important APIs/types/functions: `cbmem_entry` stores the mapped buffer and size. `mem_read()` and `mem_write()` implement the binary attribute. `address_show()` and `size_show()` expose metadata. `cbmem_entry_probe()` maps `dev->cbmem_entry.address`/`entry_size` using `devm_memremap()`.

Control flow: The coreboot bus matches `LB_TAG_CBMEM_ENTRY`. Probe allocates per-device state, stores it with `dev_set_drvdata()`, maps the firmware memory, and lets default groups expose attributes. Reads use `memory_read_from_buffer()`, while writes update the mapped buffer within bounds.

State and persistence behavior: State is per coreboot device and devm-managed. Writes to the mapped CBMEM region mutate firmware memory visible through the sysfs file, but the driver itself does not persist metadata.

Dependencies and integration points: Depends on `coreboot_table.h`, coreboot table enumeration, sysfs binary attributes, and memory remapping. It exports each CBMEM entry as `/sys/bus/coreboot/devices/cbmem-<id>/`.

Risks and test signals: Writable CBMEM is admin-only but still risky because firmware-provided memory contents are mutable from userspace. Bounds checks protect sysfs writes, but invalid firmware addresses or sizes can map wrong memory. Test by booting with CBMEM entries, reading size/address/mem, verifying partial reads/writes, and checking behavior on malformed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/cbmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.c

Purpose: Implements a `coreboot` bus and platform driver that maps the firmware coreboot table and creates one Linux device per table entry for other Google firmware drivers to bind.

Important APIs/types/functions: `coreboot_table_header` models the LBIO header. Bus callbacks are `coreboot_bus_match()`, `coreboot_bus_probe()`, `coreboot_bus_remove()`, and `coreboot_bus_uevent()`. Public exports are `__coreboot_driver_register()` and `coreboot_driver_unregister()`. `coreboot_table_populate()` creates `coreboot_device` instances.

Control flow: Init registers the bus and platform driver. Probe obtains the memory resource from ACPI `GOOGCB00`/`BOOT0000` or DT `compatible = "coreboot"`, maps the header, validates signature `LBIO`, maps the full table, iterates entries, copies raw entry data into allocated device storage, names CBMEM entries specially, and registers devices. Remove unregisters all bus devices.

State and persistence behavior: State consists of registered bus devices and copied firmware table entries. Firmware memory is read-only from this driver and unmapped after enumeration.

Dependencies and integration points: Integrates ACPI, OF, platform resources, the Linux driver core, and downstream coreboot drivers for CBMEM, framebuffer, memconsole, and VPD. Uevents expose `MODALIAS=coreboot:t%08X` for module autoloading.

Risks and test signals: The implementation validates entry size but does not verify header/table checksums. A malformed table could stop enumeration or create incorrect devices. Test with ACPI and DT discovery, multiple entry types, module autoload via modalias, remove/unbind cleanup, and corrupt signature/short entry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.h

Purpose: Provides the internal coreboot bus interface shared by Google firmware drivers.

Important APIs/types/functions: `coreboot_device` embeds a `struct device` plus a union of possible coreboot table entry payloads (`coreboot_table_entry`, `lb_cbmem_ref`, `lb_cbmem_entry`, `lb_framebuffer`, or raw bytes). `coreboot_driver` wraps probe/remove callbacks, a `device_driver`, and an ID table. `dev_to_coreboot_device()`, `coreboot_driver_register()`, `__coreboot_driver_register()`, `coreboot_driver_unregister()`, and `module_coreboot_driver()` form the driver API.

Control flow: No independent runtime flow. Drivers include this header, declare `coreboot_device_id` tables, and use `module_coreboot_driver()` to bind to devices created by `coreboot_table.c`.

State and persistence behavior: No state here. The union layout determines how downstream drivers interpret copied firmware table entries.

Dependencies and integration points: Depends on `<linux/coreboot.h>` and the device model. Used by CBMEM, framebuffer, memconsole-coreboot, and VPD drivers.

Risks and test signals: Because the union overlays raw firmware data, every consumer must match on tag before using a typed member and respect entry sizes. Test signals are compile coverage for all consumers and runtime binding to each supported coreboot tag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c

Purpose: Converts a coreboot framebuffer table entry into a platform framebuffer device when Linux did not already receive usable `screen_info`.

Important APIs/types/functions: `framebuffer_parent_pci_dev()` tries to identify an enabled display PCI device owning the framebuffer resource. `framebuffer_probe()` validates the `lb_framebuffer`, builds a memory resource, chooses either `coreboot-framebuffer` platform data for DRM corebootdrm or legacy `simple-framebuffer` data, and registers the platform device.

Control flow: The driver binds to `CB_TAG_FRAMEBUFFER`. Probe first exits if sysfb already handles screen info, then rejects empty or invalid physical addresses. It sizes the resource from `y_resolution * bytes_per_line`, finds an optional PCI parent, and registers the platform device with the framebuffer table payload or simplefb-compatible geometry.

State and persistence behavior: The driver creates a child platform device and holds a temporary PCI device reference while registering. It does not own the framebuffer memory contents.

Dependencies and integration points: Integrates the coreboot bus, PCI, sysfb, platform devices, simplefb format tables, and optionally DRM corebootdrm. Downstream display drivers consume the registered platform device.

Risks and test signals: Geometry and format matching must be exact for simplefb fallback. Resource overflow or invalid firmware dimensions could produce bad reservations. Test on coreboot systems with and without `screen_info`, with DRM corebootdrm enabled and disabled, and verify parent PCI reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/gsmi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/gsmi.c

Purpose: Implements the Google SMI firmware interface on supported x86/ACPI/DMI platforms. It provides sysfs controls for firmware event logs/config clearing, logs shutdown reasons during reboot/oops/panic, logs S0ix suspend/resume events, and can register an EFI variable backend using GSMI NVRAM commands.

Important APIs/types/functions: `gsmi_device` stores the platform device, three DMA32-accessible SMI buffers, lock, SMI command port, handshake type, and slab cache. `gsmi_exec()` performs inline assembly SMI calls and translates firmware return codes. EFI callbacks are `gsmi_get_variable()`, `gsmi_get_next_variable()`, and `gsmi_set_variable()`. Sysfs handlers include `eventlog_write()`, `gsmi_clear_eventlog_store()`, and `gsmi_clear_config_store()`.

Control flow: Init validates DMI/FADT, checks for a GSMI handler, registers a platform device/driver, creates DMA32 buffers, probes handshake mode, creates `/sys/firmware/gsmi`, optionally registers efivars, and installs reboot/die/panic notifiers. SMI calls serialize on `gsmi_dev.lock`, populate parameter/data/name buffers, invoke callback `0xef`, and interpret return codes. Exit unregisters notifiers, efivars, sysfs files, buffers, cache, and platform devices.

State and persistence behavior: State is global and includes preallocated buffers used even during panic paths. Firmware event logs, config, NVRAM variables, and S0ix logs are persistent firmware/platform state. `gsmi_shutdown_reason()` tracks logged reasons to avoid duplicates.

Dependencies and integration points: Depends on x86 ACPI FADT SMI command, DMI, EFI efivars core, sysfs firmware kobjects, notifiers, suspend callbacks, DMA32 slab allocation, and direct port I/O assembly.

Risks and test signals: SMI execution is platform-specific and can hang if handshake detection is wrong. Panic callback avoids taking a held spinlock, but notifier context remains sensitive. Buffer size is fixed at 1024 bytes, constraining EFI variable names/data. Test on supported Google/coreboot boards, verify sysfs writes, EFI variable operations, shutdown reason logging, S0ix logging opt-out, module unload cleanup, and old/quirky board rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/gsmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-coreboot.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-coreboot.c

Purpose: Exposes the coreboot CBMEM console ring buffer as `/sys/firmware/log` through the shared memconsole infrastructure.

Important APIs/types/functions: `cbmem_cons` models the firmware console header and ring data. `memconsole_coreboot_read()` maps logical reads over either a linear buffer or wrapped ring-buffer segments. `memconsole_probe()` maps the CBMEM console and registers the shared sysfs binary file.

Control flow: On a coreboot device with tag `CB_TAG_CBMEM_CONSOLE`, probe temporarily maps the header to read size, then maps the full buffer using devm memory remap. It calls `memconsole_setup()` with the ring-buffer read function and creates sysfs via `memconsole_sysfs_init()`. Remove calls `memconsole_exit()`.

State and persistence behavior: Global `cbmem_console` and `cbmem_console_size` point at firmware-owned log memory. The log can change at runtime if firmware appends messages; the driver deliberately rereads cursor on each access.

Dependencies and integration points: Depends on coreboot table bus, memory remapping, and the shared `memconsole.c` sysfs layer.

Risks and test signals: Firmware-controlled cursor/size can race with reads; size is read once to reduce overrun risk. Test with non-wrapped and wrapped logs, concurrent firmware logging if available, short/offset sysfs reads, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-coreboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-x86-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-x86-legacy.c

Purpose: Locates legacy Google BIOS memory console descriptors in the x86 EBDA and exposes the associated log through `/sys/firmware/log`.

Important APIs/types/functions: `biosmemcon_ebda` models v1 and v2 EBDA descriptors. `memconsole_ebda_init()` scans EBDA byte-by-byte for v1/v2 signatures. `found_v1_header()` and `found_v2_header()` compute base address and length, then call `memconsole_setup()`. `memconsole_x86_init()` gates discovery on Google DMI matches.

Control flow: Module init checks DMI board vendor, gets EBDA physical address, reads EBDA length, scans for magic signatures, configures a read callback over the discovered physical buffer, and creates the shared sysfs file. Exit removes the sysfs file.

State and persistence behavior: Global `memconsole_baseaddr` and `memconsole_length` track the discovered BIOS log buffer. The driver reads firmware-owned memory and does not persist changes.

Dependencies and integration points: Uses x86 EBDA helpers, DMI, ACPI includes, physical-to-virtual mapping for low memory, and the shared memconsole layer.

Risks and test signals: EBDA scanning trusts the EBDA length and descriptor fields; malformed firmware can point to invalid memory. Test on legacy Google systems with v1 and v2 descriptors, absent EBDA, absent signature, and offset reads from `/sys/firmware/log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-x86-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.c

Purpose: Provides the architecture-independent sysfs wrapper for firmware memory console logs.

Important APIs/types/functions: `memconsole_setup()` stores a backend read callback in the binary attribute private field. `memconsole_sysfs_init()` creates `/sys/firmware/log`. `memconsole_exit()` removes it. The binary attribute `memconsole_bin_attr` is read-only.

Control flow: Platform-specific discovery code calls `memconsole_setup()` before `memconsole_sysfs_init()`. Sysfs reads dispatch through `memconsole_read()` to the registered backend callback, returning `-EIO` if no callback has been installed.

State and persistence behavior: Static binary attribute state holds one callback pointer. The code does not store log contents; backends read firmware memory.

Dependencies and integration points: Used by coreboot and x86 legacy memconsole drivers. Depends on `firmware_kobj`, sysfs binary attributes, and module exports.

Risks and test signals: Only one global log file/callback exists, so simultaneous backend registration would conflict. Test signals include backend setup before sysfs creation, read behavior without a callback warning, removal cleanup, and module reference/linkage for both providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.h

Purpose: Declares the shared memconsole interface used by platform-specific firmware log providers.

Important APIs/types/functions: Declares `memconsole_setup()`, `memconsole_sysfs_init()`, and `memconsole_exit()`.

Control flow: No executable flow. Backends call setup with a read callback, initialize sysfs, and remove sysfs on teardown.

State and persistence behavior: No local state. The interface manages a global sysfs file in `memconsole.c`; providers own the memory being read.

Dependencies and integration points: Depends only on Linux basic types. Included by `memconsole-coreboot.c`, `memconsole-x86-legacy.c`, and `memconsole.c`.

Risks and test signals: The comments mention unmapping but the actual common code only removes sysfs; backend drivers must manage their own mappings. Compile coverage of all providers is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd.c

Purpose: Exposes Google Vital Product Data from coreboot CBMEM through `/sys/firmware/vpd`, including raw RO/RW sections and decoded key/value binary attributes.

Important APIs/types/functions: `vpd_cbmem` models the VPD header with magic and section sizes. `vpd_section` stores per-section mapping/sysfs state. `vpd_section_init()` maps a section, creates raw and decoded sysfs files, and marks it enabled. `vpd_section_attrib_add()` creates one sysfs binary file per valid key. `vpd_sections_init()` validates magic and initializes RO/RW sections.

Control flow: The coreboot driver binds tag `CB_TAG_VPD`, creates the top-level kobject, maps the VPD header, validates `VPD_CBMEM_MAGIC`, maps RO then RW sections if present, and decodes each section by repeatedly calling `vpd_decode_string()`. Remove destroys attributes, sections, mappings, and kobjects.

State and persistence behavior: Global `ro_vpd`, `rw_vpd`, and `vpd_kobj` store sysfs/mapping state. The driver exposes firmware-provided data as read-only sysfs attributes and does not persist writes.

Dependencies and integration points: Depends on the coreboot bus, memory remapping, sysfs binary attributes, `vpd_decode.c`, and firmware kobjects.

Risks and test signals: Section sizes and value pointers come from firmware; malformed blobs can stop decoding silently because `vpd_section_create_attribs()` ignores final decode errors. Key names with non-alnum/underscore are intentionally skipped. Test with valid RO/RW VPD, raw file reads, invalid key names, malformed length encodings, absent sections, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.c

Purpose: Decodes Google VPD length-prefixed records and invokes a callback for string key/value entries.

Important APIs/types/functions: `vpd_decode_len()` decodes a variable-length 7-bit quantity with continuation bit. `vpd_decode_entry()` consumes one length-prefixed entry and validates bounds. `vpd_decode_string()` parses record type, key, and value, then calls a user-provided callback for `VPD_TYPE_STRING`.

Control flow: Decoding starts at `*consumed`. For INFO or STRING records it increments past the type, decodes key and value entries, updates `*consumed`, and only emits callback output for STRING records. Unknown types, out-of-range lengths, and exhausted buffers return `VPD_FAIL`.

State and persistence behavior: Stateless except for updating the caller's `consumed` offset. It does not allocate or copy data; callback receives pointers into the original input buffer.

Dependencies and integration points: Used by `vpd.c` to create sysfs attributes from VPD blobs. Depends on constants and callback typedef from `vpd_decode.h`.

Risks and test signals: Integer underflow is mitigated by repeated `max_len - consumed` checks, but callers must pass valid `consumed` pointers and immutable buffers. Test length encodings at boundaries, truncated entries, INFO records, terminator/implicit terminator behavior, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.h

Purpose: Defines the public interface and constants for Google VPD decoding.

Important APIs/types/functions: Enumerates `VPD_OK`/`VPD_FAIL` and VPD record types including terminator, string, info, and implicit terminator. Defines `vpd_decode_callback` and declares `vpd_decode_string()`.

Control flow: No executable flow. Consumers pass a buffer, consumed offset, callback, and callback argument to the decoder.

State and persistence behavior: No state. The callback contract passes borrowed pointers into caller-owned VPD storage.

Dependencies and integration points: Depends on Linux integer types. Included by `vpd.c` and implemented by `vpd_decode.c`.

Risks and test signals: Callback callers must not assume null-terminated key/value strings. ABI is internal to the module composite. Test signals are compiler type checking and parser unit-style tests with binary VPD blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/Kconfig

Purpose: Defines NXP i.MX firmware driver configuration for DSP IPC, legacy SCU mailbox RPC, and newer SCMI protocol wrapper drivers.

Important APIs/types/functions: Symbols are `IMX_DSP`, `IMX_SCU`, `IMX_SCMI_CPU_DRV`, `IMX_SCMI_LMM_DRV`, and `IMX_SCMI_MISC_DRV`. Dependencies select mailbox support, SoC bus support, and ARM MXC/compile-test availability.

Control flow: No runtime flow. The settings determine whether host-to-DSP mailbox, SCFW mailbox RPC, and SCMI CPU/LMM/MISC helper exports are built.

State and persistence behavior: No state. Build choices decide which firmware communication stacks and exported helper APIs are available to platform drivers.

Dependencies and integration points: Integrates i.MX mailbox controller support, `SOC_BUS`, SCMI protocol framework, and platform-specific firmware headers.

Risks and test signals: Incorrect default/module choices can leave dependent drivers without exported symbols or probe sequencing. Test allmodconfig, ARCH_MXC default builds, modular SCMI wrappers, and compile-test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/Makefile

Purpose: Maps i.MX firmware Kconfig symbols to objects.

Important APIs/types/functions: Builds `imx-dsp.o`, legacy SCU components (`imx-scu.o misc.o imx-scu-irq.o rm.o imx-scu-soc.o`), and SCMI wrappers (`sm-cpu.o`, `sm-misc.o`, `sm-lmm.o`).

Control flow: No runtime flow. Kbuild includes objects according to selected config symbols.

State and persistence behavior: No state. Object grouping controls which exported symbols and initcalls are present.

Dependencies and integration points: Integrates with i.MX Kconfig. The SCU group is built as one logical feature because helper files depend on the core `imx_scu_call_rpc()` implementation.

Risks and test signals: The SCMI object lines use `obj-${CONFIG_...}` syntax, which should be checked against standard Kbuild expectations (`obj-$(CONFIG_...)`). Test signals include building each SCMI symbol as module/built-in and confirming expected objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-dsp.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-dsp.c

Purpose: Implements host-side mailbox doorbell IPC for i.MX DSP firmware. It provides exported helpers for DSP clients to request/free channels and ring DSP doorbells.

Important APIs/types/functions: `imx_dsp_ring_doorbell()` sends a mailbox message on a channel. `imx_dsp_request_channel()` and `imx_dsp_free_channel()` manage channels by generated names. `imx_dsp_handle_rx()` dispatches replies or requests to client callbacks. `imx_dsp_setup_channels()` initializes `txdb0`, `txdb1`, `rxdb0`, and `rxdb1`.

Control flow: Probe inherits the parent OF node, allocates `imx_dsp_ipc`, sets up mailbox clients with nonblocking sends and RX callback, requests all channels, and stores drvdata. RX channel index 0 calls `handle_reply`; index 1 calls `handle_request` and rings doorbell 1 as acknowledgement. Remove frees channels and names.

State and persistence behavior: State is per-device `imx_dsp_ipc` with channel descriptors. No persistent storage; mailbox messages coordinate with DSP firmware and external shared memory owned by clients.

Dependencies and integration points: Depends on Linux mailbox framework and `linux/firmware/imx/dsp.h` callback contracts. Built as a platform driver named `imx-dsp`.

Risks and test signals: The driver assumes client `ops` callbacks are installed before RX arrives. Error unwind must free names/channels. Test mailbox probe deferral, request/free exported helpers, RX reply/request callbacks, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-irq.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-irq.c

Purpose: Handles SCU general interrupt notifications over mailbox and exposes notifier/status helpers plus a sysfs wakeup source report.

Important APIs/types/functions: Exports `imx_scu_irq_register_notifier()`, `imx_scu_irq_unregister_notifier()`, `imx_scu_irq_get_status()`, `imx_scu_irq_group_enable()`, and `imx_scu_enable_general_irq_channel()`. Message structs encode SCU IRQ status and enable RPC calls. `scu_irq_wakeup` tracks masks and wakeup status for nine groups.

Control flow: `imx_scu_enable_general_irq_channel()` derives the MU resource id from DT mailbox phandle, gets the global SCU IPC handle, allocates a mailbox client, requests `gip3`, creates `/sys/firmware/scu_wakeup_source/wakeup_src`, and initializes work. RX callback schedules work; work queries each IRQ group, records wake source, wakes the system, and calls registered notifiers.

State and persistence behavior: Global IPC handle, work item, notifier chain, wakeup kobject, MU resource id, and wakeup masks persist for the SCU lifetime. Firmware IRQ enable state is changed via RPC.

Dependencies and integration points: Depends on SCU RPC core, mailbox, DT aliases, firmware kobjects, PM wakeup, and blocking notifier chains.

Risks and test signals: `wakeup_source_show()` can return uninitialized/last buffer contents if no wakeup source is set. Group bounds are not explicitly checked in `imx_scu_irq_group_enable()`. Test IRQ enable/disable per group, mailbox events, notifier delivery, suspend wakeup reporting, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-soc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-soc.c

Purpose: Queries i.MX SCU firmware for SoC identity, revision, unique ID, and registers a Linux SoC device.

Important APIs/types/functions: `imx_scu_soc_uid()` sends MISC unique-id RPC and composes a 64-bit ID. `imx_scu_soc_id()` reads the system ID control. `imx_scu_soc_name()` maps known ID values to i.MX8QM/i.MX8QXP/i.MX8DXL strings. `imx_scu_soc_init()` builds `soc_device_attribute` and registers the SoC device.

Control flow: Called from SCU core probe after IPC initialization. It gets the SCU handle, allocates soc attributes, reads the root DT model, queries firmware ID/UID, formats family, machine, SoC ID, revision, and serial number, then calls `soc_device_register()`.

State and persistence behavior: Uses global `imx_sc_soc_ipc_handle` and registers a SoC device. Firmware identity is read-only.

Dependencies and integration points: Depends on SCU MISC RPCs, OF root model property, sys_soc, and the SCU core handle exported by `imx-scu.c`.

Risks and test signals: Unknown SoC IDs return string `"NULL"`, which may be undesirable in sysfs. Revision bit formatting must match SCFW encoding. Test on supported i.MX8 variants, absent model property, SCU RPC failures, and `soc` sysfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu.c

Purpose: Implements the core i.MX System Controller Unit mailbox RPC transport over MU channels.

Important APIs/types/functions: `imx_sc_ipc` stores channels, lock, completions, response buffer, and fast-IPC flag. Exports `imx_scu_get_handle()` and `imx_scu_call_rpc()`. Internal callbacks `imx_scu_tx_done()` and `imx_scu_rx_callback()` coordinate mailbox send/receive. `imx_scu_ipc_write()` sends RPC words sequentially.

Control flow: Probe detects fast IPC from mailbox controller compatible, requests TX/RX mailbox channels, initializes completions and mutex, publishes the global IPC handle, initializes SoC info and general IRQ channel, then populates child OF devices. RPC calls lock the IPC, install the message pointer, send all words, wait up to 3 seconds for response if requested, translate SCU error code in `hdr->func`, clear state, and unlock.

State and persistence behavior: Global `imx_sc_ipc_handle` represents the default SCU channel. Per-call transient state includes `msg`, `rx_size`, and `count`; these are protected by the mutex.

Dependencies and integration points: Depends on mailbox framework, SCU firmware RPC headers, OF platform population, SoC init helper, IRQ helper, and downstream SCU service helpers (`misc.c`, `rm.c`).

Risks and test signals: RX before `msg` is set is ignored; timeouts must leave state consistent. Fast IPC receives all words in one callback; non-fast IPC relies on per-word channel ordering enforced by completions. Test normal RPCs, timeouts, firmware error mapping, fast/non-fast controllers, probe deferral, and child device population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/misc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/misc.c

Purpose: Provides exported client-side helpers for i.MX SCU MISC and PM RPC services.

Important APIs/types/functions: `imx_sc_misc_set_control()` sets a miscellaneous control for a resource. `imx_sc_misc_get_control()` reads one. `imx_sc_pm_cpu_start()` starts or stops a CPU resource at a physical address. Message structs model set/get control and CPU start requests/responses.

Control flow: Each helper fills an `imx_sc_rpc_msg` header with version, service, function, and size, populates request fields, then calls `imx_scu_call_rpc()` with response expected. Get-control casts the response overlay and returns `val` to the caller.

State and persistence behavior: Stateless locally. Firmware control values, resource state, and CPU start state are persistent/firmware-managed effects of the RPC.

Dependencies and integration points: Depends on `linux/firmware/imx/svc/misc.h`, SCU RPC core, and consumers needing resource controls or CPU boot management.

Risks and test signals: Incorrect message size or packed layout breaks SCFW ABI. Callers must pass valid IPC handles and resource/control IDs. Test with known controls, invalid resources, CPU start/stop paths, and SCU error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/rm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/rm.c

Purpose: Exposes i.MX SCU Resource Management RPC helpers for ownership checks and owner lookup.

Important APIs/types/functions: `imx_sc_rm_is_resource_owned()` sends `IMX_SC_RM_FUNC_IS_RESOURCE_OWNED` and returns the firmware boolean from `hdr->func`. `imx_sc_rm_get_resource_owner()` sends `IMX_SC_RM_FUNC_GET_RESOURCE_OWNER` and returns the partition number through `pt`.

Control flow: Both helpers fill packed SCU RM messages and invoke `imx_scu_call_rpc()` with a response. Ownership check intentionally ignores the return code because firmware encodes only 0/1 in the response field.

State and persistence behavior: Stateless. Reads SCU resource ownership state; does not mutate ownership.

Dependencies and integration points: Depends on SCU RPC core and `linux/firmware/imx/svc/rm.h`. Used by platform drivers that need to confirm partition access to SCU-managed resources.

Risks and test signals: Ignoring the transport return in `imx_sc_rm_is_resource_owned()` can hide IPC failures as false/garbage ownership if the response is invalid. Test owned/unowned resources, invalid resource IDs, and IPC failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/rm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-cpu.c

Purpose: Provides exported convenience wrappers for the i.MX SCMI CPU protocol.

Important APIs/types/functions: Exports `scmi_imx_cpu_reset_vector_set()`, `scmi_imx_cpu_start()`, and `scmi_imx_cpu_started()`. Probe obtains `scmi_imx_cpu_proto_ops` and a protocol handle for `SCMI_PROTOCOL_IMX_CPU`.

Control flow: The SCMI driver binds to the protocol device named `imx-cpu`. Probe rejects duplicate initialization, retrieves protocol ops via `devm_protocol_get()`, and stores globals. Exported functions return `-EPROBE_DEFER` until probe succeeds, validate pointer arguments where needed, and call protocol ops.

State and persistence behavior: Global `imx_cpu_ops` and `ph` are process-wide module state. Firmware CPU reset vector/start state is changed through SCMI.

Dependencies and integration points: Depends on SCMI core, NXP SCMI protocol definitions, and `linux/firmware/imx/sm.h` consumers.

Risks and test signals: Global singleton design assumes one i.MX CPU SCMI provider. There is no explicit remove cleanup, relying on module/SCMI lifecycle. Test probe deferral, duplicate provider rejection, invalid `started` pointer, CPU start/stop, and reset vector programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-lmm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-lmm.c

Purpose: Provides exported wrappers for i.MX SCMI Logical Machine Management operations.

Important APIs/types/functions: Exports `scmi_imx_lmm_info()`, `scmi_imx_lmm_reset_vector_set()`, and `scmi_imx_lmm_operation()`. Probe obtains `scmi_imx_lmm_proto_ops` for `SCMI_PROTOCOL_IMX_LMM`.

Control flow: The SCMI driver binds to `imx-lmm`, prevents duplicate initialization, and stores protocol ops/handle. Callers can query LMM info, program a reset vector, or request boot, power-on, or shutdown; unsupported operation enum values return `-EINVAL`.

State and persistence behavior: Global ops/handle state. Firmware logical-machine state is changed by SCMI calls and persists according to firmware semantics.

Dependencies and integration points: Depends on SCMI protocol framework and NXP LMM protocol definitions. Exported symbols are consumed by other i.MX platform drivers managing auxiliary machines/cores.

Risks and test signals: Singleton globals and no remove reset mirror other SCMI wrappers. Test probe deferral, invalid info pointer, each operation enum, shutdown flags, and duplicate SCMI device handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-lmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-misc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-misc.c

Purpose: Provides exported wrappers and debug/event integration for the i.MX SCMI MISC protocol.

Important APIs/types/functions: Exports `scmi_imx_misc_ctrl_set()` and `scmi_imx_misc_ctrl_get()`. `scmi_imx_misc_ctrl_probe()` retrieves `scmi_imx_misc_proto_ops`, registers event notifiers for `nxp,ctrl-ids`, requests notification enablement, and creates debugfs `scmi_imx/syslog`. `syslog_show()` reads firmware syslog through the protocol and dumps hex.

Control flow: Probe validates SCMI handle, prevents duplicate init, gets protocol ops/handle, parses pairs of control IDs and flags from DT, registers a dummy notifier callback for each, requests notifications, creates debugfs directory/file, and registers a devm cleanup action. Exported get/set calls defer until probe and forward to protocol ops.

State and persistence behavior: Global ops/handle and notifier block. Firmware misc control values and notification subscriptions persist in SCMI firmware for the driver lifetime.

Dependencies and integration points: Depends on SCMI core notify ops, OF properties, debugfs, seq_file, and NXP SCMI MISC protocol definitions.

Risks and test signals: If `nxp,ctrl-ids` is absent, `of_property_count_u32_elems()` can return a negative value; modulo handling should be checked. Notification callback is intentionally a no-op, so event payloads are not surfaced. Test DT parsing, odd control list rejection, notification registration failures, syslog read size, debugfs cleanup, and exported get/set before/after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft.c

Purpose: Parses the iSCSI Boot Firmware Table and exposes boot initiator, NIC, target, and ACPI table metadata through the iSCSI boot sysfs infrastructure.

Important APIs/types/functions: Packed table structs model iBFT control, initiator, NIC, and target records. Show/check callbacks include `ibft_attr_show_initiator()`, `ibft_attr_show_nic()`, `ibft_attr_show_target()`, `ibft_attr_show_acpitbl()`, and corresponding `ibft_check_*_for()` mode filters. `ibft_register_kobjects()` scans control offsets and creates iscsi boot kobjects.

Control flow: Module init finds the table via legacy ISA reservation or ACPI signatures, validates revision and checksum, creates an `iscsi_boot_kset`, scans control offsets, validates each supported record, creates initiator/NIC/target kobjects, and adds a NIC-to-PCI device sysfs link when possible. Exit removes NIC links and destroys the kset.

State and persistence behavior: Global `ibft_addr` points to firmware/ACPI table memory and `boot_kset` owns sysfs objects. The driver reads firmware boot configuration only; no persistent writes.

Dependencies and integration points: Depends on ACPI, optional legacy finder, PCI, iscsi_boot_sysfs, and network/iSCSI boot conventions. It consumes `ibft_phys_addr` exported by `iscsi_ibft_find.c` when enabled.

Risks and test signals: String offsets and lengths are firmware-controlled and need the existing table bounds checks to remain effective. CHAP secrets are exposed if present by design, so sysfs permissions matter. Test ACPI and legacy discovery, checksum failure, invalid control offsets, IPv4-mapped and IPv6 address formatting, PCI link creation, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft_find.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft_find.c

Purpose: Finds and reserves a legacy BIOS iBFT/BIFT table in low memory before ACPI parsing, for non-UEFI systems.

Important APIs/types/functions: Exports `ibft_phys_addr`. `reserve_ibft_region()` scans physical memory from `IBFT_START` to `IBFT_END` in 16-byte increments, skipping VGA memory, looking for `iBFT` or `BIFT` signatures.

Control flow: The routine exits immediately on EFI boot because iBFT 1.03 requires UEFI systems to use ACPI. Otherwise it early-maps one page at a time, compares signatures, reads table length at signature+4, checks that the table stays below the scan limit, records the physical address, reserves the aligned length with memblock, logs the address, and unmaps the last page.

State and persistence behavior: Sets global `ibft_phys_addr` and reserves the firmware table memory in memblock. It does not alter table contents.

Dependencies and integration points: Depends on early memremap, memblock, EFI boot detection, architecture low-memory constants, and `iscsi_ibft.c`, which later maps `ibft_phys_addr` to virtual memory.

Risks and test signals: Signature/length probing trusts low memory contents enough to reserve a region. Page boundary mapping must remain correct when a signature is near the end of a page. Test BIOS boot with legacy iBFT, UEFI skip behavior, VGA gap skip, invalid lengths beyond 1 MiB, and memblock reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft_find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/memmap.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/memmap.c

Purpose: Maintains the firmware memory map exposed under `/sys/firmware/memmap`, including early boot entries and hotplug-added/removed entries.

Important APIs/types/functions: `firmware_map_entry` stores start/end/type, list node, and kobject. Public APIs are `firmware_map_add_early()`, `firmware_map_add_hotplug()`, and `firmware_map_remove()`. Sysfs attributes expose `start`, `end`, and `type`. `firmware_memmap_init()` publishes early entries at late init.

Control flow: Early callers allocate entries from memblock and add them to `map_entries`. Late init creates the memmap kset and sysfs kobjects for existing entries. Hotplug add reuses bootmem-backed entries from `map_entries_bootmem` when possible or allocates a new entry, then creates sysfs immediately. Remove deletes from the active list and drops the kobject reference, with bootmem-backed storage saved for reuse by the release method.

State and persistence behavior: Persistent kernel state includes active and reusable firmware map entry lists protected by spinlocks. The driver mirrors firmware/platform memory ranges but does not change actual firmware memory.

Dependencies and integration points: Depends on firmware-map API, memblock, kobjects/ksets under `firmware_kobj`, memory hotplug hooks, and sysfs.

Risks and test signals: Callers must use exclusive end addresses; internally entries store inclusive end. Locking around find/add/remove and kobject release/reuse is subtle. Test early entries appearing after late init, hot-add/hot-remove/re-add reuse, duplicate add behavior, sysfs attribute formatting, and removal of missing entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/memmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/meson/Kconfig

Purpose: Defines the Amlogic Meson secure monitor driver configuration.

Important APIs/types/functions: `MESON_SM` is a tristate depending on `ARCH_MESON || COMPILE_TEST`, defaulting on Meson, and requiring `ARM64_4K_PAGES`.

Control flow: No runtime flow. It controls whether `meson_sm.o` is compiled.

State and persistence behavior: No state. The setting determines availability of secure monitor calls and exported helpers for efuse/chip-id/power control consumers.

Dependencies and integration points: Coordinates with ARM64 page-size constraints and the Meson firmware subsystem.

Risks and test signals: The 4K page dependency matters because secure monitor shared memory mapping assumptions may not hold for other page sizes. Test Meson defconfig, allmodconfig, and compile-test coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/meson/Makefile

Purpose: Builds the Amlogic secure monitor driver object.

Important APIs/types/functions: `obj-$(CONFIG_MESON_SM) += meson_sm.o`.

Control flow: No runtime flow. Kbuild includes the object according to `CONFIG_MESON_SM`.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with `meson/Kconfig` and the firmware build subtree.

Risks and test signals: Build-only risk. Test built-in and module builds of `CONFIG_MESON_SM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/meson_sm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/meson/meson_sm.c

Purpose: Provides an Amlogic Meson secure monitor interface for SMC calls, shared-memory read/write operations, child device population, and serial-number sysfs exposure.

Important APIs/types/functions: `meson_sm_chip` maps abstract command indexes to SMC IDs and shared-memory base commands. `meson_sm_firmware` stores chip data and mapped in/out shared memory. Exports `meson_sm_call()`, `meson_sm_call_read()`, `meson_sm_call_write()`, and `meson_sm_get()`. `serial_show()` reads chip ID data.

Control flow: Probe matches a DT compatible, maps secure monitor shared-memory bases by calling SMC commands, stores firmware state, populates child OF devices, and exposes `serial`. Generic call lookup translates command indexes to SMC IDs, then calls `arm_smccc_smc()`. Read/write helpers move data through shared memory and validate firmware-reported sizes.

State and persistence behavior: Per-platform-device firmware state holds ioremapped shared memory and chip command table. Secure monitor state is external and can include efuse/chip/power-control effects depending on command.

Dependencies and integration points: Depends on ARM SMCCC, OF/platform devices, ioremap, sysfs device groups, and public Meson firmware headers. Consumers obtain a firmware pointer via DT node with `meson_sm_get()`.

Risks and test signals: Shared memory mappings are manually unmapped only on probe failure paths; devm does not manage them after success. Size-zero read semantics intentionally copy the full requested buffer for some commands. Test SMC command lookup failures, read/write size bounds, serial sysfs output, child device population, and probe failure unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/meson/meson_sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/microchip/Kconfig

Purpose: Defines the Microchip PolarFire SoC Auto Update firmware upload driver configuration.

Important APIs/types/functions: `POLARFIRE_SOC_AUTO_UPDATE` is a tristate depending on `POLARFIRE_SOC_SYS_CTRL` and selecting `FW_LOADER` plus `FW_UPLOAD`.

Control flow: No runtime flow. The option controls whether the Auto Update driver is compiled.

State and persistence behavior: No direct state, but enabling it allows Linux to write FPGA bitstreams to SPI flash through firmware upload.

Dependencies and integration points: Integrates the Microchip system controller, firmware loader/upload framework, and MTD flash access.

Risks and test signals: Because the feature can reprogram FPGA images, dependencies must ensure the system controller and upload framework are present. Test built-in/module builds and absence/presence of system controller support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/microchip/Makefile

Purpose: Builds the Microchip PolarFire SoC Auto Update driver.

Important APIs/types/functions: `obj-$(CONFIG_POLARFIRE_SOC_AUTO_UPDATE) += mpfs-auto-update.o`.

Control flow: No runtime flow. Kbuild includes the object according to the Kconfig setting.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with Microchip firmware Kconfig and the platform firmware build.

Risks and test signals: Build-only risk; test module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/mpfs-auto-update.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/microchip/mpfs-auto-update.c

Purpose: Implements firmware-upload support for Microchip PolarFire SoC Auto Update, writing bitstream images or bitstream-info descriptors to SPI flash and asking the system controller to verify upgrade images.

Important APIs/types/functions: `mpfs_auto_update_priv` stores system controller, MTD flash, uploader handle, calculated bitstream slot size, and cancel state. Upload ops are `mpfs_auto_update_prepare()`, `mpfs_auto_update_write()`, `mpfs_auto_update_poll_complete()`, and `mpfs_auto_update_cancel()`. Helpers query availability, set the SPI directory, write flash regions, and verify images.

Control flow: Probe gets the system controller and flash, checks Auto Update availability via a security-service command, then registers a firmware uploader named `mpfs-auto-update`. Prepare computes slot size from flash size/erase size and rejects oversized images. Write distinguishes bitstream-info headers from bitstreams, updates the SPI directory for bitstreams, erases/writes the target flash region, honors cancellation after write, and verifies bitstreams through the system controller.

State and persistence behavior: Driver state is per-platform-device. Persistent effects include erasing/writing SPI flash directory, design info, and upgrade image regions. Cancel state is boolean and does not interrupt an in-progress MTD operation.

Dependencies and integration points: Depends on Microchip system controller transactions, MTD, firmware upload framework, firmware loader, debugfs include, cleanup attributes, and flash layout conventions from PolarFire programming docs.

Risks and test signals: This path can brick/update FPGA boot images if offsets or slot sizing are wrong. Directory read-modify-write must preserve unrelated eraseblock contents. Availability bit interpretation is security-sensitive. Test with fake MTD/sys controller, insufficient flash, erase-size alignment, info-vs-bitstream detection, directory already correct, partial MTD writes, verification failure, cancellation, and remove unregistering uploader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/microchip/mpfs-auto-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/mtk-adsp-ipc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/mtk-adsp-ipc.c

Purpose: Implements MediaTek ADSP mailbox IPC plumbing for clients that exchange requests and replies with audio DSP firmware.

Important APIs/types/functions: `mtk_adsp_ipc_send()` sends a 32-bit mailbox message on a selected channel and is exported GPL. `mtk_adsp_ipc_recv()` dispatches mailbox RX callbacks to client `handle_reply` or `handle_request`. Probe requests named channels `rx` and `tx`.

Control flow: Built-in platform probe inherits the parent OF node, allocates `mtk_adsp_ipc`, initializes two mailbox clients, requests channels by name, stores drvdata, and logs debug initialization. RX callbacks switch on channel index and call client ops. Remove frees all mailbox channels.

State and persistence behavior: Per-device state stores channel descriptors and client ops pointer. No persistent storage; mailbox messages coordinate with DSP runtime state.

Dependencies and integration points: Depends on mailbox framework and `linux/firmware/mediatek/mtk-adsp-ipc.h`. Higher-level ADSP clients install ops and use the exported send helper.

Risks and test signals: Like the i.MX DSP path, RX assumes `ipc->ops` callbacks are valid. Error unwind frees earlier channels. Test probe deferral, send invalid index, reply/request dispatch, absent client ops handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/mtk-adsp-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/psci/Kconfig

Purpose: Defines build options for ARM PSCI firmware support and the optional PSCI checker.

Important APIs/types/functions: `ARM_PSCI_FW` is the base bool. `ARM_PSCI_CHECKER` depends on PSCI firmware, CPU hotplug, CPU idle, and excludes torture tests.

Control flow: No runtime flow in this file. It controls inclusion of PSCI core and checker objects.

State and persistence behavior: No state. Enabling checker causes startup validation of PSCI hotplug and suspend behavior elsewhere.

Dependencies and integration points: Integrates with ARM firmware, CPU hotplug, CPU idle, and test/torture configuration.

Risks and test signals: Checker can interfere with CPU torture tests, hence the explicit dependency exclusion. Test Kconfig resolution for architectures selecting `ARM_PSCI_FW` and checker enable/disable combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/psci/Makefile

Purpose: Maps PSCI configuration symbols to build objects.

Important APIs/types/functions: Builds `psci.o` for `CONFIG_ARM_PSCI_FW` and `psci_checker.o` for `CONFIG_ARM_PSCI_CHECKER`.

Control flow: No runtime flow. Kbuild includes the PSCI core and optional checker based on config.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with `psci/Kconfig` and the ARM firmware driver subtree.

Risks and test signals: Build-only risk. Test with PSCI core alone and with checker enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/psci/Makefile -->
