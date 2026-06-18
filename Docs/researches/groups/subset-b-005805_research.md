# subset-b-005805 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl2.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl2.h

Purpose: Defines packed ACPICA C layouts, signatures, enums, and bit masks for a large set of “additional” ACPI tables used by platform, firmware, interrupt-controller, RAS, NVDIMM, audio, IOMMU, memory-topology, ARM, RISC-V, LoongArch, Intel TDX, and device-driver code. ACPICA itself does not directly consume all of these tables, but drivers and the AML/disassembler rely on exact ABI definitions.

Important APIs, types, and functions: Exports no functions; the public surface is table signatures such as `ACPI_SIG_IORT`, `ACPI_SIG_MADT`, `ACPI_SIG_NFIT`, `ACPI_SIG_NHLT`, `ACPI_SIG_PCCT`, `ACPI_SIG_PPTT`, `ACPI_SIG_RASF`, `ACPI_SIG_RAS2`, `ACPI_SIG_RHCT`, `ACPI_SIG_RIMT`, `ACPI_SIG_SDEV`, `ACPI_SIG_SWFT`, and `ACPI_SIG_TDEL`, plus packed structs for AEST, AGDI, APMT, BDAT, CCEL, ERDT, IORT, IOVT, IVRS, KEYP, LPIT, MADT, MCFG, MCHI, MPAM, MPST, MSCT, MRRM, MSDM, NFIT, NHLT, PCCT, PDTT, PHAT, PMTT, PPTT, PRMT, RASF, RAS2, RGRT, RHCT, RIMT, SBST, SDEI, SDEV, SVKL, SWFT, and TDEL. Notable helper macros include NFIT device-handle build/extract macros and many flag masks for interrupt polarity, cache attributes, PCC status, RAS commands, secure devices, and NVDIMM capabilities.

Control flow: This header does not execute control flow. Consumers parse ACPI table blobs by reading a common `acpi_table_header`, walking subtable headers and offsets, casting to the appropriate packed structure, and interpreting variable-length trailing arrays such as IORT node data, MADT subtables, NFIT flush addresses, NHLT endpoint/format lists, ERDT records, and SDEV vendor/component payloads.

State and persistence: All structures model firmware-persistent ACPI table bytes. `#pragma pack(1)` is central: any padding change would alter the ABI. Flexible arrays and offset fields represent variable persisted payloads; no kernel state is stored by this header.

Dependencies and integration points: Depends on core ACPICA table types such as `struct acpi_table_header`, `struct acpi_subtable_header`, `struct acpi_subtbl_hdr_16`, and `struct acpi_generic_address`. Integrates with ARM SMMU/GIC/IORT code, x86 and LoongArch/RISC-V interrupt discovery, PCI ECAM setup, NVDIMM/NFIT, Intel audio NHLT, PCC mailbox users, RAS/APEI, memory topology/NUMA, MPAM/RDT-like resource-control code, and firmware-health consumers.

Risks and test signals: Risks are ABI drift from spec revisions, incorrect variable-length walking, trusting reserved or offset fields, endian/packing mistakes, and exposing stale or invalid firmware resources. Test with table parser unit tests, `iasl`/ACPICA table dumps, booting machines or QEMU images with MADT/IORT/NFIT/NHLT/PCCT variants, malformed length/offset fuzzing, cross-architecture build coverage, and exact `sizeof`/offset checks for structures consumed by drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl3.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl3.h

Purpose: Provides packed ACPI table definitions for another group of platform tables, especially NUMA locality, serial console redirection, IPMI, TPM/TCG logs, virtual I/O translation, watchdogs, Windows platform/security tables, and Xen environment data.

Important APIs, types, and functions: Exports signature macros including `ACPI_SIG_SLIT`, `ACPI_SIG_SPCR`, `ACPI_SIG_SPMI`, `ACPI_SIG_SRAT`, `ACPI_SIG_TCPA`, `ACPI_SIG_TPM2`, `ACPI_SIG_VIOT`, `ACPI_SIG_WDAT`, `ACPI_SIG_WDDT`, `ACPI_SIG_WDRT`, `ACPI_SIG_WPBT`, `ACPI_SIG_WSMT`, and `ACPI_SIG_XENV`. Major structs include `acpi_table_slit`, `acpi_table_spcr`, `acpi_table_spmi`, `acpi_table_srat` and SRAT affinity subtables, TCPA client/server trailers, TPM2 revision-3/revision-4 layouts and ARM SMC trailer, VIOT node descriptors, watchdog action/resource descriptors, WPBT handoff metadata, WSMT mitigation flags, and Xen grant/event fields.

Control flow: No runtime logic is implemented. Consumers use table signatures, revisions, subtable type enums, count/offset fields, and table-specific flags to discover devices or firmware behavior. SRAT walkers derive CPU/memory/I/O proximity domains; SPCR initializes early console; TPM and TCPA consumers locate control blocks and event logs; watchdog drivers interpret action instruction entries.

State and persistence: The file models firmware-persistent table bytes and no mutable kernel state. Tables expose persistent configuration such as NUMA affinities, TPM log physical addresses, watchdog register programming sequences, and hypervisor grant/event resources.

Dependencies and integration points: Uses ACPICA common headers and `acpi_generic_address`. Integrates with NUMA initialization, console/serial early boot, IPMI/SPMI, TPM CRB/TIS/SMC paths, virtio-IOMMU discovery through VIOT, watchdog frameworks, Windows compatibility/security reporting, and Xen ACPI plumbing.

Risks and test signals: Risks include incorrect packed layout, misinterpreting SRAT flags or proximity domains, unsafe physical log/control addresses, invalid watchdog instruction masks, and start-method-specific TPM parsing mistakes. Test by dumping and parsing firmware tables, booting with known SRAT/SLIT/TPM2/SPCR/VIOT fixtures, malformed count/offset fuzzing, watchdog action validation, and cross-platform build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actypes.h -->
# sources/distributed-fs/ceph-client/include/acpi/actypes.h

Purpose: Defines the common ACPICA scalar types, pointer/size/address abstractions, object model, event/status constants, operation-region identifiers, callback signatures, buffer conventions, and utility macros used by the ACPI core and OS integration layer.

Important APIs, types, and functions: Key exports include `acpi_status`, `acpi_name`, `acpi_string`, `acpi_handle`, `acpi_size`, `acpi_io_address`, `acpi_physical_address`, `union acpi_object`, `struct acpi_object_list`, `struct acpi_buffer`, `struct acpi_device_info`, handler typedefs such as `acpi_gpe_handler`, `acpi_notify_handler`, `acpi_adr_space_handler`, `acpi_walk_callback`, and `acpi_exception_handler`, plus constants for ACPI object types, S/D/C power states, notify codes, GPE dispatch flags, address-space IDs, PM bit-register IDs, and `_STA` bits.

Control flow: Compile-time control flow selects 32-bit or 64-bit ACPICA behavior from `ACPI_MACHINE_WIDTH`, optionally narrows physical addresses with `ACPI_32BIT_PHYSICAL_ADDRESS`, and redirects allocation macros to either no-allocation stubs, debug-tracking allocators, or OS services. Runtime behavior is encoded as callback contracts and macros such as `ACPI_TIME_AFTER`, pointer arithmetic helpers, name-segment comparison/copy, acquire/release buffer conventions, and `ACPI_ALLOCATE_BUFFER`.

State and persistence: The header owns no state but defines state shapes used everywhere: ACPI namespace object data, memory mappings, system statistics, device IDs, connection contexts, PCC/FFH region contexts, and memory-cache descriptors. These are transient kernel/ACPICA state rather than firmware persistence.

Dependencies and integration points: Requires the platform/compiler headers to define machine width, calling conventions, and compiler-dependent integer types. It underpins ACPICA interpreter, namespace, table, event, OS services, device enumeration, operation regions, and Linux ACPI driver interfaces.

Risks and test signals: Risks are machine-width mismatches, pointer truncation, accidental inclusion without platform setup, object type value drift, misaligned name operations on strict-alignment CPUs, and callback ABI mismatches. Test with 32-bit and 64-bit builds, ACPI disabled/enabled builds, ACPICA unit tests, object evaluation covering every `union acpi_object` variant, and compiler warnings around pointer casts and packed data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acuuid.h -->
# sources/distributed-fs/ceph-client/include/acpi/acuuid.h

Purpose: Centralizes ACPI UUID/GUID string constants for controllers, devices, interfaces, TPM functions, NVDIMM/NFIT range/device types, processor properties, and miscellaneous device properties.

Important APIs, types, and functions: Exports only macros such as `UUID_GPIO_CONTROLLER`, `UUID_PCI_HOST_BRIDGE`, `UUID_CONTROL_METHOD_BATTERY`, `UUID_NFIT_DIMM`, `UUID_PERSISTENT_MEMORY`, `UUID_CACHE_PROPERTIES`, `UUID_DEVICE_PROPERTIES`, `UUID_DEVICE_GRAPHS`, and `UUID_USB4_CAPABILITIES`.

Control flow: No control flow. Consumers compare or publish UUID strings in `_DSD`, NFIT, device property, TPM, battery, USB4, graph, and platform-capability paths.

State and persistence: Values are immutable ABI identifiers mirrored from ACPI/device specifications. Firmware may persist these UUIDs in tables or namespace packages; the header stores no runtime state.

Dependencies and integration points: Deliberately standalone. It integrates with ACPICA table decoding, Linux ACPI property parsing, NVDIMM/NFIT code, TPM physical-presence/memory-clear flows, and device graph/property helpers.

Risks and test signals: Risks are typo-induced ABI mismatches and case/format-sensitive comparisons in consumers. Test by validating known UUID strings against spec fixtures and by probing firmware/device property paths that depend on each identifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acuuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/apei.h -->
# sources/distributed-fs/ceph-client/include/acpi/apei.h

Purpose: Declares the Linux ACPI Platform Error Interface entry points and ERST ioctl ABI used for firmware error record storage and hardware error source setup.

Important APIs, types, and functions: Defines `APEI_ERST_INVALID_RECORD_ID`, `APEI_ERST_CLEAR_RECORD`, `APEI_ERST_GET_RECORD_COUNT`, `enum hest_status`, globals `hest_disable`, `erst_disable`, and conditionally `ghes_disable`. Declares `acpi_hest_init()`, `acpi_ghes_init()`, ERST operations `erst_write()`, `erst_get_record_count()`, record-id iteration, `erst_read()`, `erst_read_record()`, `erst_clear()`, and arch hooks `arch_apei_enable_cmcff()` and `arch_apei_report_mem_error()`.

Control flow: Initialization stubs collapse to no-ops when APEI/GHES configs are disabled. Enabled users initialize HEST/GHES, iterate or read ERST records, and clear/write records through firmware-backed storage.

State and persistence: ERST records are persistent firmware error records with CPER payloads. The header exposes disable flags and record IDs but stores no records itself.

Dependencies and integration points: Depends on `linux/acpi.h`, CPER definitions, and ioctl encoding. Integrates with GHES, HEST parsing, EDAC/RAS reporting, persistent error logs, and arch-specific corrected-machine-check or memory-error reporting.

Risks and test signals: Risks include ioctl ABI breakage, ERST iteration races, invalid CPER length handling, and config-disabled callers assuming real support. Test APEI enabled/disabled builds, ERST read/write/clear through user ABI, malformed CPER injection, GHES boot paths, and arch hook coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/apei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/battery.h -->
# sources/distributed-fs/ceph-client/include/acpi/battery.h

Purpose: Defines the ACPI battery class name, notification codes, and hook registration API for auxiliary drivers that attach behavior to ACPI battery power-supply devices.

Important APIs, types, and functions: Exports `ACPI_BATTERY_CLASS`, notify values `ACPI_BATTERY_NOTIFY_STATUS`, `ACPI_BATTERY_NOTIFY_INFO`, and `ACPI_BATTERY_NOTIFY_THRESHOLD`, `struct acpi_battery_hook`, and registration functions `battery_hook_register()`, `battery_hook_unregister()`, and `devm_battery_hook_register()`.

Control flow: Hook users register callbacks; the battery core calls `add_battery()` when a matching `power_supply` is available and `remove_battery()` during teardown. The devm variant binds lifetime to a device.

State and persistence: Hook state is list-linked via `struct list_head` in each hook. Battery status/capacity is external ACPI/power-supply state, not persisted here.

Dependencies and integration points: Depends on Linux device, list, and power-supply APIs. Integrates with ACPI battery driver, platform extensions, vendor drivers, and power-management notification handling.

Risks and test signals: Risks are hook lifetime bugs, missing remove callbacks, list corruption, and incorrect behavior when battery devices appear/disappear during suspend/resume. Test hook registration/unregistration, devm cleanup, ACPI notify events `0x80`-`0x82`, hotplug/removal, and disabled extension modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/button.h -->
# sources/distributed-fs/ceph-client/include/acpi/button.h

Purpose: Provides ACPI button hardware IDs and the lid-state query API used by power-management and input/display code.

Important APIs, types, and functions: Defines `ACPI_BUTTON_HID_POWER`, `ACPI_BUTTON_HID_LID`, `ACPI_BUTTON_HID_SLEEP`, and `acpi_lid_open()`. If `CONFIG_ACPI_BUTTON` is unavailable, `acpi_lid_open()` is an inline stub returning open.

Control flow: Enabled builds call into the ACPI button driver for current lid state. Disabled builds force callers down a non-blocking “lid open” path.

State and persistence: Runtime lid state lives in the ACPI button driver/device, not this header.

Dependencies and integration points: Integrates with ACPI device matching, input subsystem, display backlight/panel policy, suspend handling, and platform power-button events.

Risks and test signals: Risks include stale lid state, callers caching disabled-stub behavior, and policy differences when the button driver is modular or absent. Test HID matching, lid open/close notifications, suspend/resume with closed lid, and builds without `CONFIG_ACPI_BUTTON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/button.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/cppc_acpi.h -->
# sources/distributed-fs/ceph-client/include/acpi/cppc_acpi.h

Purpose: Declares Linux CPPC library data structures and APIs used by CPU frequency and scheduler-performance code to read and program ACPI Collaborative Processor Performance Control registers.

Important APIs, types, and functions: Defines CPPC revision/count constants, PCC masks and commands, register indexes `enum cppc_regs`, packed `struct cpc_reg`, `struct cpc_register_resource`, `struct cpc_desc`, capability/control/feedback structs, and per-CPU `struct cppc_cpudata`. When `CONFIG_ACPI_CPPC_LIB` is enabled it declares getters/setters for performance caps, counters, desired/min/max/energy performance, EPP, auto-selection/action-window, perf-limited bits, FFH read/write, PSD mapping, fast-switch capability, and AMD preferred-core helpers; otherwise it returns `-EOPNOTSUPP`, `-ENODEV`, or false stubs.

Control flow: Consumers probe `_CPC`, classify each register as integer, system-memory, PCC, or FFH, then use the declared APIs to read feedback counters or write controls. PCC operations use command/status masks; FFH operations are delegated to arch support.

State and persistence: Per-CPU CPPC descriptors cache register resources, virtual mappings, PSD domains, and kobjects. Actual performance controls are hardware/firmware state exposed through ACPI registers and PCC shared memory.

Dependencies and integration points: Depends on Linux ACPI, cpufreq, CPPC/PCC, processor PSD structures, raw spinlocks, kobjects, cpumasks, and AMD-specific performance discovery. Integrates with `acpi-cpufreq`, `amd-pstate`, scheduler frequency invariance, thermal frequency limits, and platform firmware.

Risks and test signals: Risks include wrong register index ordering, unsafe RMW locking, PCC timeout/status handling, disabled-config callers, frequency/performance conversion errors, and AMD preferred-core misdetection. Test `_CPC` parsing, PCC and FFH register paths, concurrent cpufreq writes, EPP/autonomous mode toggles, suspend/resume, hotplug, and no-CPPC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/cppc_acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/ghes.h -->
# sources/distributed-fs/ceph-client/include/acpi/ghes.h

Purpose: Defines Generic Hardware Error Source runtime structures, severity constants, notifier registration APIs, and helpers for walking APEI generic error status records.

Important APIs, types, and functions: Exports `struct ghes`, `struct ghes_estatus_node`, `struct ghes_estatus_cache`, severities `GHES_SEV_*`, vendor-record notifier APIs, `ghes_get_devices()`, `ghes_estatus_pool_region_free()`, `ghes_estatus_pool_init()`, report-chain registration, SEA notification, helpers `acpi_hest_get_version()`, `acpi_hest_get_payload()`, `acpi_hest_get_error_length()`, `acpi_hest_get_size()`, `acpi_hest_get_record_size()`, `acpi_hest_get_next()`, and macro `apei_estatus_for_each_section()`.

Control flow: GHES instances are created from HEST generic sources and then service timer, IRQ, SCI, NMI, or SEA notifications. Error status records are walked section-by-section using revision-sensitive header sizes; vendor sections may be sent to notifier chains.

State and persistence: `struct ghes` owns mapped error-status blocks, handler identity, flags, timers/IRQs/list nodes, and device linkage. Error status caches use atomics and RCU to coalesce or defer records. Persistent record storage is ERST/CPER outside this header.

Dependencies and integration points: Depends on APEI, HED, ACPI HEST/CPER structures, notifiers, RCU, llist, timers, IRQs, and devices. Integrates with RAS reporting, EDAC, memory failure handling, firmware-first error processing, and vendor error consumers.

Risks and test signals: Risks include malformed section lengths causing bad iteration, NMI/IRQ context allocation constraints, stale mapped status blocks, notifier lifetime issues, and severity misclassification. Test GHES-enabled/disabled builds, synthetic CPER injection, v2/v3 section parsing, SEA paths, vendor notifier registration, RCU cache freeing, and panic/recoverable severity handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/ghes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/hed.h -->
# sources/distributed-fs/ceph-client/include/acpi/hed.h

Purpose: Declares the ACPI Hardware Error Device notifier API used by APEI/GHES and other firmware-first error consumers.

Important APIs, types, and functions: Exports `register_acpi_hed_notifier()` and `unregister_acpi_hed_notifier()` for `struct notifier_block`.

Control flow: Clients register notifier blocks; HED event handling invokes them when ACPI hardware error notifications arrive.

State and persistence: Notifier-chain state is owned by the HED implementation. No persistent data is represented here.

Dependencies and integration points: Depends on Linux notifier API. Integrates with GHES, ACPI error devices, and platform RAS reporting.

Risks and test signals: Risks are notifier ordering/lifetime bugs and missing unregister during module/device teardown. Test notifier registration failures, event delivery, unregister races, and ACPI HED absent builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/hed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/nfit.h -->
# sources/distributed-fs/ceph-client/include/acpi/nfit.h

Purpose: Provides the small public NFIT helper API used outside the NVDIMM/ACPI NFIT driver.

Important APIs, types, and functions: Declares `nfit_get_smbios_id(u32 device_handle, u16 *flags)` when `CONFIG_ACPI_NFIT` is enabled; otherwise provides an inline `-EOPNOTSUPP` stub.

Control flow: Consumers pass an NFIT device handle and receive SMBIOS identity/flags from the ACPI NFIT implementation if available.

State and persistence: Persistent state is firmware NFIT/SMBIOS information; this header has no state.

Dependencies and integration points: Integrates with NVDIMM, persistent memory, and platform inventory/health reporting code.

Risks and test signals: Risks include callers ignoring `-EOPNOTSUPP`, stale handles after device removal, and mismatched NFIT handle decoding. Test enabled/disabled builds, known DIMM handles, absent SMBIOS mappings, and NVDIMM hotplug/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/nfit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/nhlt.h -->
# sources/distributed-fs/ceph-client/include/acpi/nhlt.h

Purpose: Declares helpers for parsing and searching ACPI NHLT audio topology tables, including endpoint and audio format iteration over variable-length payloads.

Important APIs, types, and functions: Exports pointer helpers `acpi_nhlt_endpoint_fmtscfg()`, endpoint/format iteration macros `for_each_nhlt_endpoint()`, `for_each_nhlt_fmtcfg()`, `for_each_nhlt_endpoint_fmtcfg()`, global table get/put APIs, endpoint matching/search functions, format matching functions, and `acpi_nhlt_endpoint_mic_count()`. Disabled builds return `AE_NOT_FOUND`, `NULL`, false, or zero.

Control flow: Iteration walks `endpoints_count`, using each endpoint `length`, then finds the formats block after endpoint capabilities and steps formats by each format’s config size. Search helpers match link type, device type, direction, bus id, channel count, sample rate, valid bits, and bits per sample.

State and persistence: NHLT bytes are firmware-provided table state. An optional global mapped table is reference-managed by get/put APIs to avoid repeated map/unmap overhead in sound drivers.

Dependencies and integration points: Depends on ACPI table types, overflow-safe pointer arithmetic expectations, and Intel/SOF/HDA audio drivers. Integrates with DMIC/SSP/SoundWire endpoint discovery and microphone geometry parsing.

Risks and test signals: Risks include malformed lengths causing overrun, endpoint count mismatch, OED-config skipping errors, disabled stubs hiding missing audio topology, and invalid microphone array metadata. Test with real NHLT dumps, malformed tables, endpoint/format matching unit tests, global table reference balance, and no-`CONFIG_ACPI_NHLT` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/nhlt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/pcc.h -->
# sources/distributed-fs/ceph-client/include/acpi/pcc.h

Purpose: Defines the Linux Platform Communications Channel mailbox abstraction and shared-memory command/status bits used by ACPI PCC consumers.

Important APIs, types, and functions: Exports `struct pcc_mbox_chan`, `PCC_SIGNATURE`, command/status flag macros, `MAX_PCC_SUBSPACES`, and `pcc_mbox_request_channel()`/`pcc_mbox_free_channel()` with `-ENODEV` stubs when `CONFIG_PCC` is disabled.

Control flow: Clients request a PCC subspace by id through the mailbox framework, then use shared-memory base/size and timing metadata to issue commands and wait for completion or platform notification.

State and persistence: Runtime state is a mailbox channel, mapped shared memory, platform timing limits, and firmware-owned status/command words. ACPI PCCT table data describes the persistent channel layout.

Dependencies and integration points: Depends on mailbox controller/client APIs and ACPI PCCT definitions. Integrates with CPPC, RAS, platform firmware channels, and drivers using PCC doorbells.

Risks and test signals: Risks include subspace id overflow, missing PCC support, shared-memory mapping lifetime, status-bit races, and consumers ignoring latency/turnaround limits. Test request/free paths, disabled builds, concurrent PCC clients, command-complete/error handling, and PCCT malformed subspaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/pcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acenv.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/acenv.h

Purpose: Selects ACPICA host/compiler configuration, defines environment feature defaults, and includes the correct compiler and OS platform headers before common ACPICA types are used.

Important APIs, types, and functions: Defines configuration constants such as `ACPI_BINARY_SEMAPHORE`, `ACPI_OSL_MUTEX`, debugger threading modes, application/tool feature macros, default compiler-dependent integer types, mutex/global-lock defaults, calling-convention macros, C-library/file abstractions, and `ACPI_INIT_FUNCTION`.

Control flow: Preprocessor logic detects ACPICA tools, libraries, GCC/MSVC, Linux, BSD, EFI, Zephyr, Windows, and other environments. Unknown targets trigger `#error`. Defaults fill in symbols not defined by the selected platform.

State and persistence: No runtime state; it controls compile-time feature state such as local cache use, debug output, hardware reduction, disassembler/debugger inclusion, and C-library usage.

Dependencies and integration points: Includes `acgcc.h`, `aclinux.h`, `aczephyr.h`, or other platform files. It is the first-stage configuration dependency for `actypes.h`, ACPICA OSL, tools, and Linux ACPI integration.

Risks and test signals: Risks include wrong target detection, conflicting tool/kernel macros, missing `ACPI_MACHINE_WIDTH`, and unintended debug/allocation behavior. Test kernel and userspace ACPICA builds, tool builds (`iasl`, `acpi_exec`, dump tools), Zephyr/EFI paths when relevant, and unknown-target failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acenvex.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/acenvex.h

Purpose: Adds second-stage host/compiler extensions after ACPICA headers have been included, letting OS and compiler backends override or clean up definitions that depend on earlier declarations.

Important APIs, types, and functions: Includes `aclinuxex.h` for Linux, optional DragonFly/EFI extension headers, and `acgccex.h` or MSVC equivalents for compiler-specific cleanup.

Control flow: Compile-time dispatch chooses OS extension first and compiler extension second. There is no runtime behavior.

State and persistence: No state; it mutates the preprocessor environment.

Dependencies and integration points: Depends on the platform macros established by `acenv.h`. Integrates with ACPICA OSL declarations and compiler quirks.

Risks and test signals: Risks are missing late overrides for alternate prototypes or compiler builtins, and inclusion-order regressions. Test Linux kernel/userspace ACPICA builds and builds that exercise GCC extension cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acenvex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acgcc.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/acgcc.h

Purpose: Supplies GCC-specific ACPICA compiler definitions, attributes, varargs support, native math flags, flexible-array workaround, and non-string annotations.

Important APIs, types, and functions: Defines `ACPI_INLINE`, `ACPI_GET_FUNCTION_NAME`, `ACPI_PRINTF_LIKE()`, `ACPI_UNUSED_VAR`, `COMPILER_VA_MACRO`, `ACPI_USE_NATIVE_MATH64`, fallback `__has_attribute`, `ACPI_FALLTHROUGH`, `ACPI_FLEX_ARRAY`, and `ACPI_NONSTRING` when supported.

Control flow: Compile-time feature detection selects attributes based on compiler support. Kernel builds include `linux/stdarg.h`; non-kernel builds include `stdarg.h`.

State and persistence: No runtime state; this changes compiler diagnostics, generated code, and structure declarations.

Dependencies and integration points: Used by all GCC ACPICA builds, including Linux kernel and ACPICA utilities. It supports packed ACPI table definitions and debug/log format checking.

Risks and test signals: Risks include attribute availability assumptions, flexible-array layout differences, and format warnings missed if `ACPI_PRINTF_LIKE` breaks. Test with multiple GCC/Clang versions, `-Wimplicit-fallthrough`, `-Wformat`, and structures using `ACPI_FLEX_ARRAY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acgccex.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/acgccex.h

Purpose: Provides extra GCC cleanup after headers are included, currently to avoid buggy macro versions of `strchr()` in some toolchains.

Important APIs, types, and functions: Undefines `strchr` if it is a macro. No functions or types are exported.

Control flow: Single preprocessor conditional executes at include time.

State and persistence: No state.

Dependencies and integration points: Included by `acenvex.h` for GCC builds. It protects ACPICA utility code such as getopt parsing from problematic libc/compiler macro substitutions.

Risks and test signals: Risks are subtle compile failures if `strchr` remains macro-expanded or if undefining it conflicts with a target C library expectation. Test ACPICA utility builds on GCC/libc combinations known to define `strchr` as a macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/acgccex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aclinux.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/aclinux.h

Purpose: Configures ACPICA for Linux kernel and Linux userspace builds, mapping ACPICA types, allocators, exports, debug defaults, include policy, and disabled-ACPI stubs to Linux conventions.

Important APIs, types, and functions: Defines Linux ACPICA feature macros, enforces `<linux/acpi.h>` inclusion for external kernel code, sets `ACPI_MACHINE_WIDTH`, `ACPI_USE_SYSTEM_INTTYPES`, `ACPI_USE_GPE_POLLING`, `ACPI_INIT_FUNCTION`, `ACPI_EXPORT_SYMBOL`, `acpi_cache_t`, lock types, `acpi_uintptr_t`, `ACPI_OFFSET`, log prefixes, alternate OSL prototype macros, and no-`CONFIG_ACPI` external-return stubs.

Control flow: Preprocessor splits kernel versus userspace. Kernel builds include Linux headers and optional asm ACPI environment, set configuration from Kconfig, and define stub bodies when ACPI is disabled. Userspace builds select standard headers and infer 32/64-bit width from architecture macros.

State and persistence: No runtime state; it controls compile-time ABI and feature availability.

Dependencies and integration points: Integrates ACPICA with Linux kernel memory allocation, spinlocks, exports, printk, PCI config, ACPI reduced hardware, debugger options, and userspace ACPICA utilities.

Risks and test signals: Risks include direct ACPICA inclusion by kernel code, wrong machine width in userspace, disabled-ACPI stubs masking calls, and mismatched alternate OSL prototypes. Test `CONFIG_ACPI=y/n`, debug and debugger configs, 32-bit/64-bit userspace tools, and include-policy compile failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aclinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aclinuxex.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/aclinuxex.h

Purpose: Supplies Linux-kernel late ACPICA OSL declarations and inline/macro implementations for allocation, object-cache allocation, thread-id retrieval, raw lock operations, debugger setup, and optional 64-bit math fallbacks.

Important APIs, types, and functions: Declares `acpi_os_initialize()` and `acpi_os_terminate()`, defines `acpi_os_allocate()`, `acpi_os_allocate_zeroed()`, `acpi_os_acquire_object()`, `acpi_os_free()`, `acpi_os_get_thread_id()`, `acpi_os_create_lock()`, `acpi_os_create_raw_lock()`, raw acquire/release/delete helpers, `acpi_os_readable()`, debugger init/terminate stubs, and math macros `ACPI_DIV_64_BY_32` and `ACPI_SHIFT_RIGHT_64` if native divide is unavailable.

Control flow: Allocators choose `GFP_ATOMIC` when interrupts are disabled and `GFP_KERNEL` otherwise. Lock creation allocates Linux spinlock/raw-spinlock objects and initializes them. Raw acquire/release save and restore interrupt flags.

State and persistence: Allocated locks and cache objects are runtime kernel memory. There is no persistent state.

Dependencies and integration points: Depends on Linux `kmalloc`, `kzalloc`, `kmem_cache_zalloc`, `kfree`, `current`, spinlocks, raw spinlocks, `do_div`, and interrupt-state helpers. Used by ACPICA OSL internals.

Risks and test signals: Risks are sleeping allocations during resume/IRQ-off paths, lockdep false positives, raw lock lifetime leaks, and math fallback errors on 32-bit systems. Test boot/resume allocation paths, ACPI table parsing under IRQ-off resume, lockdep, 32-bit non-native divide builds, and ACPI debugger stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aclinuxex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aczephyr.h -->
# sources/distributed-fs/ceph-client/include/acpi/platform/aczephyr.h

Purpose: Configures ACPICA for Zephyr builds with 64-bit width, single-threaded operation, native RSDP pointer use, system C library usage, and disabled ACPICA error/debug output.

Important APIs, types, and functions: Defines `ACPI_MACHINE_WIDTH`, `ACPI_NO_ERROR_MESSAGES`, `ACPI_USE_SYSTEM_CLIBRARY`, `ACPI_SINGLE_THREADED`, `ACPI_USE_NATIVE_RSDP_POINTER`, includes Zephyr kernel/device/fs/assert headers, and declares `acpi_enable_dbg_print(bool enable)`.

Control flow: Compile-time configuration only; runtime debug output can be toggled by the declared function.

State and persistence: No state in the header. Zephyr ACPICA runtime may maintain debug-print state behind `acpi_enable_dbg_print()`.

Dependencies and integration points: Depends on Zephyr kernel/device/filesystem/sys headers and C library headers. Integrates ACPICA with Zephyr’s platform layer.

Risks and test signals: Risks include hard-coded 64-bit assumptions, single-threaded ACPI in a multithreaded environment, and disabled diagnostics hiding firmware errors. Test Zephyr ACPICA builds, debug toggling, RSDP discovery, and table parsing on target platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/platform/aczephyr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/proc_cap_intel.h -->
# sources/distributed-fs/ceph-client/include/acpi/proc_cap_intel.h

Purpose: Defines Intel-specific processor capability bits used by OSPM to communicate supported power-management and performance-control mechanisms to firmware.

Important APIs, types, and functions: Exports bit macros such as `ACPI_PROC_CAP_P_FFH`, `ACPI_PROC_CAP_C_C1_HALT`, `ACPI_PROC_CAP_C_C1_FFH`, `ACPI_PROC_CAP_C_C2C3_FFH`, `ACPI_PROC_CAP_SMP_P_HWCOORD`, and `ACPI_PROC_CAP_COLLAB_PROC_PERF`, plus combined masks `ACPI_PROC_CAP_EST_CAPABILITY_SMP`, `ACPI_PROC_CAP_EST_CAPABILITY_SWSMP`, and `ACPI_PROC_CAP_C_CAPABILITY_SMP`.

Control flow: No runtime control flow. Processor/ACPI code ORs these bits into capability buffers passed through firmware methods such as `_PDC`.

State and persistence: Bits represent communicated capability state, not stored state in this header.

Dependencies and integration points: Integrates with ACPI processor P-state, C-state, T-state, FFH, SpeedStep/coordination, and CPPC capability negotiation on Intel processors.

Risks and test signals: Risks include advertising unsupported capabilities, failing to advertise hardware coordination, and firmware choosing bad control paths. Test `_PDC` payload generation, Intel CPU feature combinations, firmware behavior before/after capability updates, and suspend/resume processor power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/proc_cap_intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/processor.h -->
# sources/distributed-fs/ceph-client/include/acpi/processor.h

Purpose: Defines ACPI processor driver data structures and APIs for CPU enumeration, idle states, performance states, throttling, thermal limits, CPPC probing, and CPU frequency/thermal integration.

Important APIs, types, and functions: Exports HIDs, power/performance/throttling constants, domain coordination constants, register structs for C/P/T state controls, `struct acpi_processor_cx`, `struct acpi_lpi_state`, `struct acpi_processor_power`, `struct acpi_psd_package`, `struct acpi_processor_px`, `struct acpi_processor_performance`, `struct acpi_tsd_package`, `struct acpi_processor_throttling`, `struct acpi_processor_limit`, `struct acpi_processor_flags`, and `struct acpi_processor`. Declares performance registration, `_PSD` parsing, SMM notification, P-state/CPPC/idle/throttling/thermal hooks, CPU id mapping helpers, per-CPU `processors`, and `call_on_cpu()`.

Control flow: Processor discovery maps ACPI ids to logical CPUs, parses `_CST`/LPI, `_PSS`/`_PCT`/`_PSD`, `_TSS`/`_PTC`/`_TSD`, and installs idle/cpufreq/thermal hooks depending on Kconfig. `call_on_cpu()` runs directly when already on the target CPU or dispatches through `work_on_cpu()`. Disabled configs return no-op or error stubs.

State and persistence: `struct acpi_processor` stores per-processor runtime state: ACPI handle, ids, power states, performance and throttling domains, limits, thermal cooling device, device pointer, and frequency QoS requests. Firmware ACPI methods and tables are the persistent source of capabilities.

Dependencies and integration points: Depends on CPU hotplug, cpufreq, PM QoS, scheduler, SMP, thermal framework, workqueues, asm ACPI id mapping, CPPC, and architecture FFH idle support. Integrates with ACPI processor core, idle driver, cpufreq perflib, thermal cooling, and CPU invariance.

Risks and test signals: Risks include bad CPU id mapping, domain coordination errors, unsafe CPU-affine execution, stale hotplug state, incorrect disabled-config behavior, and thermal/performance limit conflicts. Test CPU hotplug, `_PPC` notifications, C/P/T-state parsing, CPPC probe/exit, FFH idle entry, thermal throttling, no-cpufreq/no-idle builds, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/reboot.h -->
# sources/distributed-fs/ceph-client/include/acpi/reboot.h

Purpose: Declares the ACPI reboot entry point with a no-op fallback for non-ACPI builds.

Important APIs, types, and functions: Exports `acpi_reboot()` when `CONFIG_ACPI` is enabled; otherwise defines an inline empty function.

Control flow: Reboot paths can call `acpi_reboot()` unconditionally and either perform ACPI reset register logic or do nothing if ACPI is unavailable.

State and persistence: No state in the header. Runtime reset state is firmware/hardware controlled.

Dependencies and integration points: Integrates with architecture machine restart paths and ACPI FADT reset-register handling.

Risks and test signals: Risks are callers assuming reboot occurred after the no-op stub, and platform reset register regressions. Test ACPI/non-ACPI builds and reboot on systems using ACPI reset versus fallback restart mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/video.h -->
# sources/distributed-fs/ceph-client/include/acpi/video.h

Purpose: Defines ACPI video/backlight public interfaces, notification codes, display type constants, brightness state structures, and backlight-selection helpers used by GPU, backlight, and platform drivers.

Important APIs, types, and functions: Exports `struct acpi_video_brightness_flags`, `struct acpi_video_device_brightness`, `ACPI_VIDEO_CLASS`, display type constants, notify values `0x80`-`0x89`, `enum acpi_backlight_type`, and APIs `acpi_video_register()`, `acpi_video_unregister()`, `acpi_video_register_backlight()`, `acpi_video_get_edid()`, `acpi_video_handles_brightness_key_presses()`, `acpi_video_get_levels()`, `__acpi_video_get_backlight_type()`, `acpi_video_get_backlight_type()`, and `acpi_video_backlight_use_native()`. Disabled builds return `-ENODEV`, vendor/native defaults, or false.

Control flow: Enabled GPU/platform drivers query the selected backlight type, optionally signal native GPU backlight availability, retrieve EDID/brightness levels, and register ACPI video support. Disabled builds steer callers to vendor/native fallbacks.

State and persistence: Runtime state includes brightness level arrays, current level, ACPI video registration, and global backlight-detection state. Firmware methods `_BCL`, `_BQC`, `_BCM`, and EDID methods provide persisted/firmware-backed data.

Dependencies and integration points: Depends on ACPI device structures, errno/types, GPU drivers, backlight class devices, input brightness key handling, and platform quirks.

Risks and test signals: Risks include incorrectly caching key-handling state, non-GPU callers invoking `acpi_video_backlight_use_native()`, malformed brightness packages, reversed/indexed brightness handling bugs, and disabled-stub policy changes. Test brightness hotkeys, native/vendor/ACPI selection on laptops, EDID retrieval, `_BCL` variants, module unload, and no-`CONFIG_ACPI_VIDEO` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/Kbuild -->
# sources/distributed-fs/ceph-client/include/asm-generic/Kbuild

Purpose: Lists mandatory generic asm headers that every architecture except UML must provide or inherit, forming the baseline architecture ABI expected by the Linux kernel.

Important APIs, types, and functions: Uses Kbuild variable `mandatory-y` to require headers such as `atomic.h`, `archrandom.h`, `barrier.h`, `bitops.h`, `uaccess.h`, `io.h`, `irq.h`, `module.h`, `pgalloc.h`, `rwonce.h`, `tlbflush.h`, `topology.h`, and many others.

Control flow: Kbuild consumes this file while preparing/generated checking architecture include trees. UML is excluded because it borrows several asm headers from the host architecture.

State and persistence: No runtime state. It persists build-system policy about required architecture header coverage.

Dependencies and integration points: Integrates with arch header generation, generic header fallbacks, `make headers_check`-style validation, and architecture port bring-up.

Risks and test signals: Risks are missing mandatory headers in new ports, adding headers here without compatible generic fallbacks, or breaking UML assumptions. Test all-arch/header builds, new architecture defconfigs, and include dependency scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/access_ok.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/access_ok.h

Purpose: Provides the generic user-pointer range validation used by architectures that do not need custom `access_ok()` behavior.

Important APIs, types, and functions: Defines fallback `TASK_SIZE_MAX`, inline `__access_ok(const void __user *ptr, unsigned long size)`, and macro `access_ok(addr, size)`.

Control flow: The check returns true for alternate user address spaces or no-MMU builds. Otherwise it validates `size <= TASK_SIZE_MAX` and `addr <= TASK_SIZE_MAX - size`, catching overflow with a single range comparison.

State and persistence: No state. It validates transient user-space access ranges.

Dependencies and integration points: Depends on `TASK_SIZE`, `CONFIG_MMU`, `CONFIG_ALTERNATE_USER_ADDRESS_SPACE`, `likely()`, and `__user` annotations. Integrates with `uaccess` copy/get/put paths.

Risks and test signals: Risks include architectures with variable compat `TASK_SIZE` not overriding `TASK_SIZE_MAX`, overflow mistakes, and false positives on special address-space architectures. Test boundary addresses, zero/large sizes, compat tasks, no-MMU builds, and hardened usercopy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/access_ok.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/agp.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/agp.h

Purpose: Supplies minimal generic AGP cache/page hooks for architectures that do not need special AGP mapping operations.

Important APIs, types, and functions: Defines `map_page_into_agp(page)` and `unmap_page_from_agp(page)` as no-ops, and `flush_agp_cache()` as `mb()`.

Control flow: No branch logic; callers get a memory barrier for cache flush and no page-specific setup.

State and persistence: No state.

Dependencies and integration points: Includes `asm/io.h` for barrier/I/O context. Integrates with AGP/GART graphics memory paths on simple architectures.

Risks and test signals: Risks are using this fallback on hardware requiring explicit cache management or AGP aperture mapping. Test AGP graphics workloads, DMA coherency, and architecture overrides for non-coherent systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/agp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/archrandom.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/archrandom.h

Purpose: Provides default no-hardware-random implementations for architecture random and seed APIs.

Important APIs, types, and functions: Defines `arch_get_random_longs()` and `arch_get_random_seed_longs()`, both `__must_check`, returning zero generated words.

Control flow: Always returns 0, signaling no architecture entropy source.

State and persistence: No state; no entropy is produced.

Dependencies and integration points: Used by the kernel random subsystem when an architecture does not override hardware random helpers.

Risks and test signals: Risks are callers ignoring the return value or assuming hardware entropy exists. Test random subsystem behavior on architectures using this fallback, boot entropy accounting, and compiler warnings for ignored `__must_check`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/asm-offsets.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/asm-offsets.h

Purpose: Forwards generic asm offset consumers to the generated `generated/asm-offsets.h` file.

Important APIs, types, and functions: Contains only `#include <generated/asm-offsets.h>`.

Control flow: Build-time include redirection only.

State and persistence: Generated offsets encode build-time structure layout constants for assembly code; this header stores none itself.

Dependencies and integration points: Depends on the kernel build having generated `asm-offsets.h`. Used by assembly and low-level code needing C structure offsets.

Risks and test signals: Risks are missing generated headers or stale offsets after structure changes. Test clean builds, incremental rebuilds touching offset-generating sources, and architecture assembly that includes the generic header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/asm-prototypes.h

Purpose: Declares generic C prototypes for memory routines that may be called from assembly or compiler-generated code, avoiding macro substitutions.

Important APIs, types, and functions: Undefines and declares `__memset`, `__memcpy`, `__memmove`, `memset`, `memcpy`, and `memmove` with `__kernel_size_t` sizes.

Control flow: No runtime logic; this is a declaration header.

State and persistence: No state.

Dependencies and integration points: Includes `linux/bitops.h` for type/dependency setup. Integrates with architecture assembly, lib/string implementations, and symbol export/CFI handling.

Risks and test signals: Risks include prototype mismatch with actual implementations, macro leakage, and calling-convention mismatch from assembly. Test builds with LTO/CFI, all architectures using generic prototypes, and string routine symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/atomic.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/atomic.h

Purpose: Implements generic 32-bit atomic integer operations for architectures that can build them from `cmpxchg` on SMP or interrupt disabling on UP.

Important APIs, types, and functions: Generates `generic_atomic_add/sub/and/or/xor`, return variants, and fetch variants, then maps them to `arch_atomic_*`. Defines `arch_atomic_read()` and `arch_atomic_set()` through `READ_ONCE`/`WRITE_ONCE`.

Control flow: On SMP, each operation loops on `arch_cmpxchg()` until the expected old value is replaced. On non-SMP, it disables local interrupts, updates `v->counter`, and restores interrupts.

State and persistence: Operates on caller-owned `atomic_t` counters. No global state.

Dependencies and integration points: Depends on `asm/cmpxchg.h`, `asm/barrier.h`, `linux/irqflags.h` for UP, and atomic wrapper layers in `linux/atomic.h`.

Risks and test signals: Risks include weak `cmpxchg` semantics on architectures, missing barriers for higher-level atomic APIs, IRQ latency on UP, and signed overflow expectations. Test atomic litmus tests, KCSAN/lockless users, SMP contention, UP interrupt nesting, and compare with architecture overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/atomic64.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/atomic64.h

Purpose: Declares a generic spinlock-backed 64-bit atomic implementation for architectures without native 64-bit atomic instructions.

Important APIs, types, and functions: Defines aligned `atomic64_t`, `ATOMIC64_INIT`, declares `generic_atomic64_read/set`, add/sub/and/or/xor operations with return/fetch variants, `generic_atomic64_dec_if_positive()`, `generic_atomic64_cmpxchg()`, `generic_atomic64_xchg()`, and `generic_atomic64_fetch_add_unless()`, then maps them to `arch_atomic64_*`.

Control flow: Implementations are external, typically serializing operations through hashed spinlocks. The header only binds generic symbols to the arch atomic64 interface.

State and persistence: Operates on caller-owned 64-bit atomic counters; any lock table is implemented elsewhere.

Dependencies and integration points: Depends on Linux types and the generic atomic64 implementation object. Used by 32-bit or simple architectures to satisfy `atomic64_*` APIs.

Risks and test signals: Risks are alignment assumptions, lock contention, release/acquire semantics of mapped operations, and missing implementation linkage. Test atomic64 selftests, 32-bit SMP stress, cmpxchg/xchg correctness, add-unless races, and module link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/atomic64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_change_attr.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/audit_change_attr.h

Purpose: Lists syscall numbers that change file attributes for generic audit syscall class construction.

Important APIs, types, and functions: Emits conditional entries for chmod/chown/fchown variants, xattr set/remove variants including `*xattrat`, `fchmodat`, `fchmodat2`, 32-bit ownership calls, and link/linkat.

Control flow: Preprocessor conditionals include only syscalls defined by the architecture ABI.

State and persistence: No runtime state. The resulting compiled audit class table is persistent kernel metadata.

Dependencies and integration points: Included by audit architecture syscall-class definitions after syscall numbers are available. Integrates with Linux audit filtering for attribute-changing operations.

Risks and test signals: Risks include missing new attribute-changing syscalls, architecture syscall-name differences, and over/under-auditing. Test audit rules for chmod/chown/xattr/link syscalls on multiple architectures and verify new syscall additions update the list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_change_attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_dir_write.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/audit_dir_write.h

Purpose: Lists directory-modifying syscall numbers for generic audit write-directory classification.

Important APIs, types, and functions: Conditionally emits `rename`, `mkdir`, `rmdir`, `creat`, `link`, `unlink`, `symlink`, `mknod`, `mkdirat`, `mknodat`, `unlinkat`, `renameat`, `linkat`, `symlinkat`, and `renameat2`.

Control flow: Compile-time syscall-number conditionals tailor the list to each architecture ABI.

State and persistence: No runtime state; contributes constants to audit class tables.

Dependencies and integration points: Used by audit syscall filters to identify directory write operations across architectures.

Risks and test signals: Risks are omitted syscalls causing audit gaps and including nonexistent syscalls causing build failures. Test audit directory watches for create/delete/rename/link operations and architecture builds with sparse syscall sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_dir_write.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_read.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/audit_read.h

Purpose: Lists syscall numbers that read filesystem metadata or extended attributes for audit read classification.

Important APIs, types, and functions: Emits `readlink`, `readlinkat`, `quotactl`, listxattr/getxattr variants including `*xattrat`, and link-specific xattr variants.

Control flow: Architecture-specific preprocessor checks include available syscall numbers.

State and persistence: No runtime state; compiled tables use the emitted constants.

Dependencies and integration points: Integrated into audit syscall-class generation.

Risks and test signals: Risks include missing modern xattr-at syscalls or classifying quotactl inconsistently. Test audit read rules against xattr, readlink, and quota queries on architectures with and without at-style syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_read.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_signal.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/audit_signal.h

Purpose: Lists signal-sending syscall numbers for generic audit signal classification.

Important APIs, types, and functions: Emits `__NR_kill`, `__NR_tgkill`, and `__NR_tkill`.

Control flow: No conditionals in this fragment; architectures including it are expected to define these syscall numbers.

State and persistence: No runtime state; entries become audit syscall class metadata.

Dependencies and integration points: Used by audit code for process signal operations.

Risks and test signals: Risks are build failures on unusual syscall sets and missing newer signal-related syscalls if the class expectations expand. Test audit signal rules for kill/tgkill/tkill and architecture syscall tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_write.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/audit_write.h

Purpose: Builds a generic audit write syscall class by including directory writes and adding other filesystem-affecting write syscalls.

Important APIs, types, and functions: Includes `audit_dir_write.h`, then emits `acct`, `swapon`, `quotactl`, truncation variants, socket `bind`, and `fallocate` where defined.

Control flow: Compile-time syscall-number checks specialize the list.

State and persistence: No runtime state; contributes to audit syscall class tables.

Dependencies and integration points: Depends on syscall numbers and directory-write fragment. Integrates with Linux audit watches and syscall filtering.

Risks and test signals: Risks include broad or narrow write classification, especially `bind` for filesystem namespace sockets and quota/fallocate effects. Test audit write rules for directory operations, truncation, fallocate, swapon, and Unix socket bind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/audit_write.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/barrier.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/barrier.h

Purpose: Provides generic memory, DMA, SMP, virtual-machine, acquire/release, conditional-load, persistent-memory, and write-combining barrier definitions for architectures that override only low-level primitives or use compiler barriers.

Important APIs, types, and functions: Defines/falls back `nop`, `mb`, `rmb`, `wmb`, `dma_mb/rmb/wmb`, `__smp_*`, `smp_mb/rmb/wmb`, `smp_store_mb`, `smp_mb__before_atomic`, `smp_mb__after_atomic`, `smp_store_release`, `smp_load_acquire`, `virt_*` barriers, `smp_acquire__after_ctrl_dep`, `smp_cond_load_relaxed`, `smp_cond_load_acquire`, `pmem_wmb`, `io_stop_wc`, and `smp_mb__after_switch_mm`.

Control flow: If an architecture provides `__mb`-style primitives, wrappers add KCSAN instrumentation. Otherwise barriers fall back to `barrier()`. SMP builds use hardware/smp barriers; UP builds reduce SMP barriers to compiler barriers while DMA and device barriers remain strict.

State and persistence: No state. It constrains ordering of memory, device, virtualized, and persistent-memory accesses.

Dependencies and integration points: Depends on compiler barriers, KCSAN hooks, `READ_ONCE`/`WRITE_ONCE`, `cpu_relax()`, and architecture overrides. Used throughout lockless kernel code, device drivers, DMA, virtualization, and persistent memory.

Risks and test signals: Risks are insufficient ordering on weak architectures, over-serialization performance loss, missing KCSAN instrumentation, and misuse of control dependencies. Test Linux memory-model litmus tests, KCSAN, DMA device tests, virtualization guest/host ordering, pmem persistence tests, and architecture-specific overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops.h

Purpose: Aggregates generic bit operation implementations for architectures that use the C-language fallback bitops stack.

Important APIs, types, and functions: Includes generic implementations for `__ffs`, `ffz`, `fls`, `__fls`, `fls64`, scheduler bitops, `ffs`, hweight, lock bitops, atomic bitops, non-atomic bitops, little-endian bitops, and ext2 atomic helpers. Enforces inclusion through `<linux/bitops.h>`.

Control flow: Include-time composition only; direct include triggers `#error` unless `_LINUX_BITOPS_H` is set.

State and persistence: No state; operations act on caller bitmaps/words.

Dependencies and integration points: Depends on irq flags, compiler helpers, barriers, and the Linux bitops wrapper. Used by bitmaps, filesystems, schedulers, locks, and drivers.

Risks and test signals: Risks include direct include misuse, mismatched atomic/non-atomic semantics, endian confusion, and architecture overrides conflicting with generic helpers. Test bitmap/bitops selftests, ext2 bitmap updates, lock bitops, and include hygiene.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/__ffs.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/__ffs.h

Purpose: Implements generic `__ffs()` to find the zero-based index of the least significant set bit in an unsigned long.

Important APIs, types, and functions: Defines `generic___ffs(unsigned long word)` and maps `__ffs(word)` to it unless the architecture provides `__HAVE_ARCH___FFS`.

Control flow: Tests progressively smaller low-bit chunks, shifting right and accumulating 32/16/8/4/2/1 offsets. Input zero is explicitly undefined and must be checked by callers.

State and persistence: No state.

Dependencies and integration points: Depends on `BITS_PER_LONG` and asm types. Used by bitmap scanning, `ffz`, and generic bitops.

Risks and test signals: Risks are zero input misuse and 32/64-bit branch errors. Test powers of two, mixed-bit words, 32-bit and 64-bit builds, and callers’ zero guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/__ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/__fls.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/__fls.h

Purpose: Implements generic `__fls()` to find the zero-based index of the most significant set bit in an unsigned long.

Important APIs, types, and functions: Defines `generic___fls(unsigned long word)` and maps `__fls(word)` unless `__HAVE_ARCH___FLS` is set.

Control flow: Starts at `BITS_PER_LONG - 1`, tests high chunks, left-shifts the word when the high chunk is empty, and subtracts offsets until the top set bit is located. Input zero is undefined.

State and persistence: No state.

Dependencies and integration points: Depends on `BITS_PER_LONG` and asm types. Used by bitmap sizing, integer log calculations, and generic bitops.

Risks and test signals: Risks are zero input misuse, top-bit edge cases, and 32/64-bit shift mistakes. Test zero-guarded callers, highest bit set, lowest bit set, random values, and both word sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/__fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/arch_hweight.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/arch_hweight.h

Purpose: Provides architecture hweight hooks that delegate to software population-count implementations.

Important APIs, types, and functions: Defines `__arch_hweight32()`, `__arch_hweight16()`, `__arch_hweight8()`, and `__arch_hweight64()` as wrappers around `__sw_hweight*`.

Control flow: Straight-line delegation.

State and persistence: No state.

Dependencies and integration points: Depends on asm types and software hweight helpers. Used by generic hweight macros and bitmap/counting code.

Risks and test signals: Risks are performance on architectures with hardware popcount but no override, and type-width mismatches. Test hweight selftests for all widths and performance-sensitive bitmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/atomic.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/atomic.h

Purpose: Implements generic atomic bit set/clear/change/test operations on bitmaps using atomic-long fetch operations.

Important APIs, types, and functions: Defines `arch_set_bit()`, `arch_clear_bit()`, `arch_change_bit()`, `arch_test_and_set_bit()`, `arch_test_and_clear_bit()`, and `arch_test_and_change_bit()`, then includes instrumented atomic bitops.

Control flow: Computes the target word with `BIT_WORD(nr)`, mask with `BIT_MASK(nr)`, performs raw atomic OR/ANDNOT/XOR or fetch variants, and returns the previous bit state for test-and operations.

State and persistence: Mutates caller-owned volatile bitmap words atomically.

Dependencies and integration points: Depends on atomic-long operations, compiler annotations, barriers, and instrumented wrappers. Used by bit locks, flags, filesystems, and concurrent bitmap code.

Risks and test signals: Risks are missing ordering expectations, volatile/atomic cast assumptions, and incorrect bit numbering. Test atomic bitops under concurrency, KCSAN instrumentation, lock bit users, and little-endian bitmap call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__ffs.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__ffs.h

Purpose: Provides a compiler-builtin implementation of `__ffs()` for architectures/toolchains that choose it over the manual generic version.

Important APIs, types, and functions: Defines `__ffs(unsigned long word)` as `__builtin_ctzl(word)`.

Control flow: Delegates entirely to the compiler builtin. Zero input remains undefined.

State and persistence: No state.

Dependencies and integration points: Depends on compiler support for `__builtin_ctzl`. Used by bitops configurations that prefer builtin codegen.

Risks and test signals: Risks include undefined zero behavior and compiler differences in builtin lowering. Test bitops selftests, zero guards, and generated code on GCC/Clang for 32-bit and 64-bit targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__fls.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__fls.h

Purpose: Provides compiler-builtin `__fls()` using count-leading-zero support.

Important APIs, types, and functions: Defines `__fls(unsigned long word)` as word width minus one minus `__builtin_clzl(word)`.

Control flow: Delegates to compiler builtin; zero input is undefined.

State and persistence: No state.

Dependencies and integration points: Depends on `__builtin_clzl` and correct `sizeof(word)` width. Used by generic bitops when builtin implementations are selected.

Risks and test signals: Risks are zero input, wrong width assumptions, and compiler lowering differences. Test boundary values, top-bit values, 32/64-bit targets, and generated assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-ffs.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-ffs.h

Purpose: Defines `ffs()` through the compiler builtin with libc-compatible one-based indexing.

Important APIs, types, and functions: Macro `ffs(x)` expands to `__builtin_ffs(x)`.

Control flow: Delegated to the compiler. Unlike `__ffs`, `ffs(0)` returns 0.

State and persistence: No state.

Dependencies and integration points: Depends on compiler `__builtin_ffs`. Used by integer and bitmap helpers expecting libc-style semantics.

Risks and test signals: Risks are confusing one-based `ffs()` with zero-based `__ffs()`. Test `ffs(0)`, `ffs(1)`, high bits, and callers converting between index conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-fls.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-fls.h

Purpose: Defines `fls()` through compiler count-leading-zero support with one-based result semantics.

Important APIs, types, and functions: Inline `fls(unsigned int x)` returns `sizeof(x) * 8 - __builtin_clz(x)` or 0 for `x == 0`.

Control flow: Explicitly handles zero, otherwise delegates to `__builtin_clz`.

State and persistence: No state.

Dependencies and integration points: Depends on compiler `__builtin_clz`. Used by power-of-two, sizing, and bitmap helpers.

Risks and test signals: Risks are one-based versus zero-based confusion and incorrect assumptions for non-`unsigned int` callers. Test zero, one, `0x80000000`, and random values against generic `fls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/const_hweight.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/const_hweight.h

Purpose: Provides compile-time and runtime population-count macros that choose constant folding when possible and architecture/software hweight otherwise.

Important APIs, types, and functions: Defines `__const_hweight8/16/32/64`, generic `hweight8/16/32/64`, constant-required `HWEIGHT8/16/32/64`, and type-invariant `HWEIGHT()`.

Control flow: `__builtin_constant_p()` selects compile-time bit counting; constant-required forms use `BUILD_BUG_ON_ZERO` to reject nonconstant arguments.

State and persistence: No state.

Dependencies and integration points: Depends on arch hweight hooks, `BUILD_BUG_ON_ZERO`, and compiler constant detection. Used by bitmask validation, static sizing, and runtime bitmap metrics.

Risks and test signals: Risks include multiple evaluation surprises for macro arguments, nonconstant misuse of `HWEIGHT*`, and width truncation. Test compile-time constant enforcement, runtime hweight equivalence, and side-effect-free usage expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/const_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic-setbit.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic-setbit.h

Purpose: Provides ext2 little-endian atomic bitmap helpers using native atomic little-endian test-and-bit operations.

Important APIs, types, and functions: Defines `ext2_set_bit_atomic(l, nr, addr)` as `test_and_set_bit_le(nr, addr)` and `ext2_clear_bit_atomic(l, nr, addr)` as `test_and_clear_bit_le(nr, addr)`.

Control flow: Ignores the lock argument and relies on atomic little-endian bitops to return the previous bit value while updating the bitmap.

State and persistence: Mutates filesystem bitmaps, often persisted to disk by ext2-like filesystems after buffer writeback.

Dependencies and integration points: Depends on little-endian atomic bitops. Used by ext2 bitmap allocation/free paths on architectures with suitable atomic LE operations.

Risks and test signals: Risks are ignoring a lock on architectures where LE atomic ops are insufficient and confusing endian order. Test ext2 block/inode bitmap allocation under concurrency and compare on big-endian systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic-setbit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic.h

Purpose: Provides spinlock-based ext2 atomic little-endian bitmap set/clear helpers for architectures that do not use direct atomic LE operations.

Important APIs, types, and functions: Defines `ext2_set_bit_atomic(lock, nr, addr)` and `ext2_clear_bit_atomic(lock, nr, addr)` using `spin_lock()`, `__test_and_set_bit_le()`/`__test_and_clear_bit_le()`, and `spin_unlock()`.

Control flow: Acquires the provided spinlock, performs a non-atomic little-endian test-and-update, releases the lock, and returns the prior bit value.

State and persistence: Mutates caller filesystem bitmaps that become persistent through filesystem writeback.

Dependencies and integration points: Depends on spinlocks and little-endian non-atomic bitops. Used by ext2 allocation/free code on generic architectures.

Risks and test signals: Risks include callers passing the wrong lock, deadlocks from lock ordering, and bitmap corruption if mixed with lockless updates. Test concurrent ext2 allocation/free, lockdep, big-endian bitmap behavior, and fsck after stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffs.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffs.h

Purpose: Implements generic `ffs()` with libc-compatible one-based indexing for the first set bit in an `int`.

Important APIs, types, and functions: Defines `generic_ffs(int x)` and maps `ffs(x)` unless the architecture provides `__HAVE_ARCH_FFS`.

Control flow: Returns 0 for zero. Otherwise shifts through 16/8/4/2/1-bit chunks and increments a one-based result until the low set bit is located.

State and persistence: No state.

Dependencies and integration points: Used by generic bitops and integer helpers where compiler builtins or arch implementations are absent.

Risks and test signals: Risks are one-based semantics confusion and signed-int expectations. Test zero, powers of two, negative/high-bit inputs, and equivalence with compiler builtin `ffs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffz.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffz.h

Purpose: Defines `ffz()` to find the zero-based index of the first zero bit in a word.

Important APIs, types, and functions: Macro `ffz(x)` expands to `__ffs(~(x))`.

Control flow: Inverts the word and delegates to `__ffs`; input with no zero bits is undefined and must be guarded by callers.

State and persistence: No state.

Dependencies and integration points: Depends on `__ffs`. Used by bitmap allocation and low-level bit scanning.

Risks and test signals: Risks include all-ones input misuse and word-size assumptions. Test zero word, all-ones guarded cases, mixed bitmaps, and allocation scans near word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffz.h -->
