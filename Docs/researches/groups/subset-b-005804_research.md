# subset-b-005804 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acbuffer.h -->
# sources/distributed-fs/ceph-client/include/acpi/acbuffer.h

## Purpose
`acbuffer.h` defines ACPICA's C representations for buffers returned by ACPI predefined names, especially `_FDE`, `_GRT`, `_GTM`, and `_PLD`, plus the `_SRT` time-setting payload. It also defines bit extraction and construction macros for the packed `_PLD` buffer format without relying on compiler-dependent C bitfield layout.

## Important APIs, types, and functions
The important exported types are `struct acpi_fde_info`, `struct acpi_grt_info`, `struct acpi_gtm_info`, and `struct acpi_pld_info`. `_PLD` support includes `ACPI_PLD_REV1_BUFFER_SIZE`, `ACPI_PLD_REV2_BUFFER_SIZE`, `ACPI_PLD_BUFFER_SIZE`, and `ACPI_PLD_GET_*`/`ACPI_PLD_SET_*` macros for revision, color, geometry, visibility, dock/lid/panel position, shape, group metadata, ejectability, cabinet/card cage, rotation/order, and revision-2 offsets. Panel constants such as `ACPI_PLD_PANEL_TOP` through `ACPI_PLD_PANEL_UNKNOWN` encode standard ACPI panel positions.

## Control flow
This header has no executable control flow. Runtime parsing happens in ACPICA interfaces such as `acpi_decode_pld_buffer`, which consumes raw AML buffer bytes and fills `struct acpi_pld_info` using these macros. Firmware construction paths may use the corresponding setters.

## State and persistence behavior
There is no owned state. The structures are transient decoded views over firmware-provided ACPI method buffers. Persistence is external: AML methods return the raw buffers and ACPICA/kernel callers allocate and free decoded results.

## Dependencies and integration points
The macros depend on bit helpers and integer masks from ACPICA core headers such as `actypes.h`. `acpixf.h` includes this file because `acpi_decode_pld_buffer()` exposes `struct acpi_pld_info`. Linux ACPI device-location helpers in `acpi_bus.h` consume the decoded `_PLD` information for physical placement and user-visible device metadata.

## Risks and test signals
Risks are mostly ABI and firmware-data risks: wrong byte ordering, incorrect revision-1 versus revision-2 length handling, field-offset drift against the ACPI specification, and callers assuming C structure packing mirrors the raw `_PLD` buffer. Test signals include decoding 16-byte and 20-byte `_PLD` buffers, validating color-ignore behavior, checking panel/position constants against known firmware, fuzzing short buffers, and round-tripping getter/setter macros on each documented bit range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acconfig.h -->
# sources/distributed-fs/ceph-client/include/acpi/acconfig.h

## Purpose
`acconfig.h` centralizes ACPICA global configuration constants, cache sizing defaults, specification limits, RSDP search windows, serial-operation-region buffer sizes, UUID formatting constants, and AML debugger buffer limits. It is the compile-time policy header that keeps common ACPICA constants consistent across the interpreter, namespace, table manager, resource manager, and tools.

## Important APIs, types, and functions
This header exports no functions. Important constants include `ACPI_OS_NAME`, cache depths such as `ACPI_MAX_STATE_CACHE_DEPTH`, checksum and reduced-hardware switches (`ACPI_CHECKSUM_ABORT`, `ACPI_REDUCED_HARDWARE`), interpreter limits such as `ACPI_MAX_SEMAPHORE_COUNT`, `ACPI_MAX_REFERENCE_COUNT`, `ACPI_MAX_SLEEP`, `ACPI_MAX_LOOP_TIMEOUT`, method argument/local counts, RSDP scan locations, operation-region space limits, SMBus/IPMI/GSBus/PRM/FFH buffer sizes, UUID string offsets, and debugger sizes/prompts.

## Control flow
There is no runtime flow here, but these definitions steer runtime behavior elsewhere. For example, table-discovery code scans the EBDA and high BIOS areas using the RSDP constants; the AML interpreter enforces method local/argument counts and loop timeouts; serial bus operation regions size status/length/data buffers from these macros.

## State and persistence behavior
The header does not store state. Its constants influence in-memory ACPICA caches and guardrails. Changing them can alter object lifetime, memory pressure, interpreter failure modes, and firmware compatibility, but no state persists across boots from this file alone.

## Dependencies and integration points
`acpixf.h` includes `acconfig.h` before public globals and interfaces. The constants integrate with ACPICA core implementation files, the Linux ACPICA build, ACPICA user-space tools, and platform headers that may override switches before inclusion. `ACPI_OS_NAME` is a particularly sensitive integration point because firmware often branches on `_OS`/`_OSI` compatibility strings.

## Risks and test signals
Risks include breaking AML compatibility by changing `_OS`, hiding firmware checksum defects if `ACPI_CHECKSUM_ABORT` stays false, increasing cache depths enough to affect memory usage, setting reduced-hardware mode incorrectly, and altering spec constants that external AML assumes. Test signals include ACPICA boot on legacy and reduced-hardware systems, RSDP discovery tests, malformed checksum behavior, interpreter loop-timeout tests, serial bus buffer bounds, and debugger command-buffer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acexcep.h -->
# sources/distributed-fs/ceph-client/include/acpi/acexcep.h

## Purpose
`acexcep.h` defines the complete `acpi_status` exception namespace for ACPICA. It classifies return codes into environmental, programmer, table, AML execution, and internal control classes, provides success/failure and class-test macros, and optionally defines the string tables used by `acpi_format_exception()` and ACPICA help/compiler tools.

## Important APIs, types, and functions
Important macros are class tags `AE_CODE_ENVIRONMENTAL`, `AE_CODE_PROGRAMMER`, `AE_CODE_ACPI_TABLES`, `AE_CODE_AML`, `AE_CODE_CONTROL`, constructors `EXCEP_ENV`/`EXCEP_PGM`/`EXCEP_TBL`/`EXCEP_AML`/`EXCEP_CTL`, `ACPI_SUCCESS`, `ACPI_FAILURE`, `AE_OK`, and class predicates such as `ACPI_AML_EXCEPTION`. The exception catalog covers common runtime failures (`AE_NO_MEMORY`, `AE_NOT_FOUND`, `AE_TIME`), API misuse (`AE_BAD_PARAMETER`), table defects (`AE_BAD_SIGNATURE`, `AE_BAD_CHECKSUM`), AML faults (`AE_AML_OPERAND_TYPE`, `AE_AML_LOOP_TIMEOUT`), and interpreter control statuses (`AE_CTRL_BREAK`, `AE_CTRL_CONTINUE`). `struct acpi_exception_info` carries names and optional descriptions.

## Control flow
There is no direct executable flow unless `ACPI_DEFINE_EXCEPTION_TABLE` is defined in one translation unit. In that build mode, the header emits static exception-name arrays by class; `acpi_format_exception()` indexes those arrays after masking the class and code. ACPICA code uses nonzero status values as error/control returns and `AE_OK` as success.

## State and persistence behavior
The header has no mutable state. With `ACPI_DEFINE_EXCEPTION_TABLE`, it contributes read-only static tables. Status values are transient function-return contracts and are not persisted.

## Dependencies and integration points
All ACPICA public and OSL interfaces use `acpi_status`, making this header a central ABI contract. `acpixf.h` exposes `acpi_format_exception()`, diagnostic macros in `acoutput.h` consume status codes, and Linux ACPI callers translate many ACPICA errors into kernel error codes or boot logs.

## Risks and test signals
Risks include changing numeric values and breaking binary/source compatibility, misclassifying control statuses as hard failures, omitting string-table entries for new codes, or treating `AE_CTRL_*` as user-visible errors. Test signals include formatting every exception, asserting class predicates, compile coverage with and without `ACPI_DEFINE_EXCEPTION_TABLE`, AML interpreter paths for loop timeout and resource errors, and callers that distinguish `AE_NOT_FOUND` from `AE_SUPPORT`/`AE_NOT_CONFIGURED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acexcep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acnames.h -->
# sources/distributed-fs/ceph-client/include/acpi/acnames.h

## Purpose
`acnames.h` collects canonical ACPI namespace method names and root path strings used across ACPICA and Linux ACPI code. It avoids duplicated string literals for common predefined methods and root namespace identifiers.

## Important APIs, types, and functions
The header exports string macros for common namespace methods such as `METHOD_NAME__ADR`, `_HID`, `_CID`, `_CRS`, `_DSD`, `_PLD`, `_PRW`, `_STA`, `_UID`, and power methods `_PS0` through `_PS3`. Root-only pathname macros include `METHOD_PATHNAME__PTS`, `METHOD_PATHNAME__SST`, and `METHOD_PATHNAME__WAK`. It also defines encoded name constants `ACPI_UNKNOWN_NAME`, `ACPI_PREFIX_MIXED`, `ACPI_PREFIX_LOWER`, `ACPI_ROOT_NAME`, and string forms such as `ACPI_ROOT_PATHNAME`, `ACPI_NAMESPACE_ROOT`, and `ACPI_NS_ROOT_PATH`.

## Control flow
There is no direct control flow. Namespace lookup, object evaluation, table loading, suspend/resume, and device enumeration code pass these names to ACPICA functions like `acpi_get_handle()` and `acpi_evaluate_object()`.

## State and persistence behavior
No state is stored. These are compile-time constants representing AML namespace names that firmware persists in DSDT/SSDT tables.

## Dependencies and integration points
`acpi.h` includes this early so later type and interface headers can refer to canonical names. Linux ACPI bus helpers and drivers use the strings to evaluate device identity, resource, power, and wake methods. The integer constants depend on ACPICA name-segment conventions and host byte ordering assumptions already handled by ACPICA.

## Risks and test signals
Risks are typographical or encoding errors that silently break namespace lookup, inconsistent root path handling, and overuse of names in contexts where methods are optional. Test signals include namespace traversal on devices with `_HID`, `_CID`, `_UID`, `_CRS`, `_DSD`, `_PLD`, suspend/resume calls to `\_PTS` and `\_WAK`, and root-name formatting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acnames.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acoutput.h -->
# sources/distributed-fs/ceph-client/include/acpi/acoutput.h

## Purpose
`acoutput.h` defines ACPICA debug component IDs, debug levels, trace flags, diagnostic macros, module/function tracing macros, and compile-time stubs for builds without debug or error output. It is the diagnostic policy and call-site instrumentation header for ACPICA.

## Important APIs, types, and functions
Important layer masks include `ACPI_UTILITIES`, `ACPI_HARDWARE`, `ACPI_EVENTS`, `ACPI_TABLES`, `ACPI_NAMESPACE`, `ACPI_PARSER`, `ACPI_DISPATCHER`, `ACPI_EXECUTER`, `ACPI_RESOURCES`, and tool/driver component masks. Debug levels range from exception levels (`ACPI_LV_INIT`, `ACPI_LV_INFO`, `ACPI_LV_REPAIR`) through tracing, allocation, parse-tree, mutex/thread/I/O/interrupt, AML disassembly, and full-table verbosity. Call-site macros include `ACPI_MODULE_NAME`, `AE_INFO`, `ACPI_INFO`, `ACPI_WARNING`, `ACPI_ERROR`, `ACPI_EXCEPTION`, `ACPI_DEBUG_PRINT`, `ACPI_FUNCTION_TRACE*`, `return_ACPI_STATUS`, `return_PTR`, and dump/trace helpers.

## Control flow
In debug builds, call sites first check `acpi_dbg_level` and `acpi_dbg_layer` via `ACPI_IS_DEBUG_ENABLED()` before calling `acpi_debug_print()` or raw print variants. Function trace macros emit entry records and return macros emit exit records before returning. In non-debug builds, tracing and debug print macros compile away; error-message macros also compile away when `ACPI_NO_ERROR_MESSAGES` is defined.

## State and persistence behavior
The header itself has no storage, but it depends on ACPICA globals `acpi_dbg_level`, `acpi_dbg_layer`, and trace globals declared in `acpixf.h`. These are runtime debug settings only and do not persist across boot.

## Dependencies and integration points
`acpixf.h` declares the actual diagnostic functions and globals. OS-specific printing is ultimately implemented through OSL functions from `acpiosxf.h`. Linux ACPI debugging, dynamic debug, firmware-bug reporting, and ACPICA interpreter traces all flow through these macros.

## Risks and test signals
Risks include side effects in macro arguments, return macros hiding control flow, debug builds changing stack usage, compiled-out diagnostics masking important failures, and inconsistent component IDs causing missing or excessive logs. Test signals include builds with `ACPI_DEBUG_OUTPUT` on/off, `ACPI_NO_ERROR_MESSAGES` on/off, variadic macro and non-variadic compiler modes, runtime toggling of debug layer/level, and trace return macros preserving return values exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acoutput.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi.h

## Purpose
`acpi.h` is the master public ACPICA include for code that interfaces with the ACPI Component Architecture. It provides a stable include order for environment definitions, names, types, exceptions, table layouts, resource descriptors, diagnostics, OS services, and public ACPICA functions.

## Important APIs, types, and functions
This file exports no independent APIs. Its important behavior is the include sequence: `platform/acenv.h`, `acnames.h`, `actypes.h`, `acexcep.h`, `actbl.h`, `acrestyp.h`, `platform/acenvex.h`, `acoutput.h`, `acpiosxf.h`, and `acpixf.h`. The order matters because later headers depend on environment macros, core typedefs, exception codes, table structures, and diagnostic definitions.

## Control flow
There is no runtime control flow. Compile-time inclusion through this file determines which declarations and macros a translation unit sees and prevents subtle ordering defects that would occur if ACPICA headers were included ad hoc.

## State and persistence behavior
No state is created. The included headers declare globals and structures used elsewhere, but `acpi.h` is only an aggregation point.

## Dependencies and integration points
Kernel ACPI code and ACPICA implementation files include this when they need the full public surface. It ties together ACPICA's OS-independent layer with Linux-specific platform headers and OSL implementations. Because it includes table definitions, resource definitions, and external interfaces, it is a high-fanout dependency.

## Risks and test signals
Risks include include-order regressions, accidental removal of a dependency that downstream files rely on, increased compile blast radius, and macro namespace collisions. Test signals include full kernel ACPI builds, standalone ACPICA tool builds, compile tests for files that include only `acpi.h`, and header self-containment checks under different platform configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h

## Purpose
`acpi_bus.h` is Linux's main ACPI bus and device-model contract. It defines ACPI device state, driver registration, scan handlers, hotplug contexts, fwnode/property integration, power and wake state, physical-device binding, dependency tracking, PCI root data, DMA/IOMMU helpers, and many utility entry points used by ACPI-aware drivers.

## Important APIs, types, and functions
Core types include `struct acpi_handle_list`, `struct acpi_hotplug_profile`, `struct acpi_scan_handler`, `struct acpi_hotplug_context`, `struct acpi_driver`, `struct acpi_device`, `struct acpi_data_node`, `struct acpi_bus_event`, `struct acpi_bus_type`, and `struct acpi_pci_root`. Important helpers include ACPI method evaluators (`acpi_evaluate_integer`, `acpi_evaluate_reference`, `acpi_execute_simple_method`, `acpi_evaluate_ej0`, `acpi_evaluate_reg`), DSM helpers (`acpi_check_dsm`, `acpi_evaluate_dsm_typed`), discovery helpers (`acpi_dev_found`, `acpi_dev_present`, `acpi_get_physical_device_location`), notify and private-data handlers, driver registration (`acpi_bus_register_driver`, `acpi_bus_unregister_driver`, `module_acpi_driver`), scan/trim APIs, power APIs, wake APIs, dependency APIs, and ACPI device matching/refcount helpers.

## Control flow
ACPI scan code creates `struct acpi_device` instances from namespace nodes, fills status/PNP/power/wakeup/property fields, and either attaches scan handlers or lets registered ACPI drivers match on IDs. Hotplug notifications flow through installed notify handlers into `struct acpi_hotplug_context` callbacks and scan handlers. Power-management paths evaluate `_PSC`, `_PSx`, power resources, wake GPEs, and PM notifiers. Device-link style dependencies are tracked through `struct acpi_dep_data` and cleared when suppliers are enumerated.

## State and persistence behavior
Most state is runtime kernel state attached to `struct acpi_device`: `_STA` status bits, flags, IDs, `_ADR`/`_UID`, current power state, wake resources and counts, physical-node bindings, fwnode properties, software nodes, dependency counts, and driver data. Persistent source-of-truth state remains firmware AML/tables; kernel state is reconstructed at boot or hotplug rescan.

## Dependencies and integration points
This header integrates ACPICA handles with the Linux driver core, `struct device`, fwnode/property APIs, procfs ACPI root, notifier chains, PCI, DMA/IOMMU configuration, PM core, wakeup sources, Kconfig-gated quirk code, and optional ACPI/PM/SLEEP/NUMA features. It is consumed by most Linux ACPI platform, bus, and device drivers.

## Risks and test signals
Risks include lifetime races between ACPI devices, fwnodes, physical devices, and notify handlers; incorrect `_STA` handling; dependency deadlocks; hotplug ordering bugs; PM wake reference leaks; UID type mismatches; Kconfig stub behavior diverging from enabled behavior; and parent-child power sequencing issues. Test signals include ACPI scan on nested namespaces, module ACPI driver bind/unbind, hotplug eject, `_DEP` supplier/consumer enumeration, DSM typed return filtering, fwnode property queries, PCI root discovery, DMA configuration, wake enable/disable, and builds with `CONFIG_ACPI` or `CONFIG_PM` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h

## Purpose
`acpi_drivers.h` provides legacy/common ACPI driver constants and declarations shared by Linux ACPI drivers, especially fabricated Linux-specific HIDs, PCI interrupt-link helpers, PCI root scanning hooks, and dock-station matching.

## Important APIs, types, and functions
Important constants include `ACPI_MAX_STRING`, Linux pseudo-HIDs such as `ACPI_POWER_HID`, `ACPI_PROCESSOR_OBJECT_HID`, `ACPI_SYSTEM_HID`, `ACPI_THERMAL_HID`, `ACPI_BUTTON_HID_POWERF`, `ACPI_BUTTON_HID_SLEEPF`, `ACPI_VIDEO_HID`, `ACPI_BAY_HID`, `ACPI_DOCK_HID`, `ACPI_ECDT_HID`, SMBus HIDs, and `ACPI_FIXED_HARDWARE_EVENT`. Public declarations include `acpi_irq_penalty_init()`, `acpi_pci_link_allocate_irq()`, `acpi_pci_link_free_irq()`, `acpi_get_pci_dev()`, `pci_acpi_scan_root()`, `pci_acpi_crs_quirks()`, and `is_dock_device()`, with Kconfig stubs where appropriate.

## Control flow
There is no local implementation. ACPI PCI code calls the interrupt-link helpers to allocate/free GSIs and trigger/polarity information. PCI root scan code calls the arch hook to add a bus. Fixed ACPI button events are translated to a synthetic notification value so fixed hardware and namespace devices can share driver paths.

## State and persistence behavior
No state is owned here. PCI interrupt-link state, dock state, and PCI device references are maintained by implementation files and driver core objects. Firmware-provided PCI routing and ACPI namespace data are the persistent inputs.

## Dependencies and integration points
The header depends on ACPI bus types and optionally PCI, x86, and ACPI dock Kconfig features. It bridges ACPI namespace devices to Linux PCI devices and legacy ACPI drivers that predate newer fwnode/property abstractions.

## Risks and test signals
Risks include pseudo-HID collisions, incorrect fixed-event notification mapping, PCI interrupt resource conflicts, stubs hiding missing PCI/dock support, and x86 CRS quirks affecting resource windows. Test signals include ACPI button devices and fixed buttons, PCI root scan on ACPI systems, PCI link allocation/free with IRQ polarity/trigger checks, SMBus HID matching including IBM quirks, and builds with `CONFIG_PCI` or `CONFIG_ACPI_DOCK` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_io.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_io.h

## Purpose
`acpi_io.h` declares Linux ACPI memory-mapping helpers used by the ACPICA OS services layer and ACPI table/register access paths. It provides a default `acpi_os_ioremap()` wrapper and APIs for mapping physical addresses and ACPI Generic Address Structures.

## Important APIs, types, and functions
The default inline `acpi_os_ioremap()` maps an ACPI physical address with `ioremap_cache()` unless an architecture supplies its own implementation. Public declarations include `acpi_permanent_mmap`, `acpi_os_map_iomem()`, `acpi_os_unmap_iomem()`, `acpi_os_get_iomem()`, `acpi_os_map_generic_address()`, and `acpi_os_unmap_generic_address()`.

## Control flow
Callers request mappings for physical ACPI memory ranges or `struct acpi_generic_address` registers. The implementation decides whether to create a transient mapping, reuse a permanent mapping, or return an existing early/late mapping. Generic-address helpers interpret GAS space IDs and map only applicable memory-backed registers.

## State and persistence behavior
The header exposes `acpi_permanent_mmap`, a runtime policy flag controlling mapping lifetime behavior. Mapping state is maintained in implementation code and the kernel ioremap subsystem; no persistent state exists.

## Dependencies and integration points
It depends on Linux `io.h`, architecture ACPI hooks from `asm/acpi.h`, ACPICA physical address types, and ACPI table/register consumers such as FADT register access, WDAT/GAS users, and `acpiosxf.h` memory I/O functions.

## Risks and test signals
Risks include cacheability mismatches, leaking permanent mappings, unmapping shared mappings incorrectly, handling zero/invalid GAS addresses, and architecture overrides diverging from generic expectations. Test signals include mapping FADT GAS registers, early table mapping and late unmapping, repeated map/unmap of the same physical range, memory versus I/O GAS handling, and architecture builds with custom `acpi_os_ioremap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h

## Purpose
`acpi_lpat.h` declares Linux helpers for ACPI LPAT conversion tables, which translate between raw sensor values and temperatures. LPAT is used by thermal and power-management code that obtains linear piecewise conversion data from firmware.

## Important APIs, types, and functions
The main data types are `struct acpi_lpat`, with `temp` and `raw` points, and `struct acpi_lpat_conversion_table`, with a point array and count. When `CONFIG_ACPI` is enabled, exported helpers are `acpi_lpat_raw_to_temp()`, `acpi_lpat_temp_to_raw()`, `acpi_lpat_get_conversion_table()`, and `acpi_lpat_free_conversion_table()`. Disabled builds provide simple stubs returning zero or `NULL`.

## Control flow
Enabled implementations obtain an LPAT package from an ACPI handle, build a conversion table, and perform interpolation or nearest-segment conversion in either direction. Callers free the allocated table after use. In non-ACPI builds, control flow short-circuits through inline stubs.

## State and persistence behavior
The conversion table is caller-owned runtime memory derived from firmware data. The raw LPAT source persists only in ACPI tables/methods; this header owns no global state.

## Dependencies and integration points
It depends on ACPI handle types and `CONFIG_ACPI`. Thermal drivers and Intel platform power/thermal code are typical consumers. The helper abstracts firmware encoding so drivers can reason in temperatures instead of device-specific raw values.

## Risks and test signals
Risks include malformed LPAT packages, non-monotonic points, divide-by-zero interpolation segments, overflow during conversion, memory leaks if callers skip `acpi_lpat_free_conversion_table()`, and misleading non-ACPI stubs returning zero. Test signals include valid multi-point tables, out-of-range raw/temp values, duplicate raw or temp points, package parse failures, and builds with `CONFIG_ACPI=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_lpat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h

## Purpose
`acpi_numa.h` declares Linux ACPI NUMA mapping helpers for translating ACPI proximity domains (PXMs) from SRAT/HMAT data into kernel NUMA node IDs. It also exposes control hooks for disabling SRAT and HMAT handling after invalid firmware data.

## Important APIs, types, and functions
When `CONFIG_ACPI_NUMA` is enabled, the header defines `MAX_PXM_DOMAINS`, declares `pxm_to_node()`, `node_to_pxm()`, `acpi_map_pxm_to_node()`, `acpi_srat_revision`, `disable_srat()`, `fix_pxm_node_maps()`, `bad_srat()`, and `srat_disabled()`. When disabled, `fix_pxm_node_maps()`, `disable_srat()`, `pxm_to_node()`, and `node_to_pxm()` become harmless stubs. `disable_hmat()` is separately gated by `CONFIG_ACPI_HMAT`.

## Control flow
SRAT parsing maps firmware proximity domains to kernel node IDs through `acpi_map_pxm_to_node()` and later resolves in both directions through `pxm_to_node()` and `node_to_pxm()`. If SRAT validation fails, callers invoke `bad_srat()` or `disable_srat()`; HMAT parsing can be disabled independently.

## State and persistence behavior
The mapping state lives in NUMA implementation files and is derived at boot from ACPI SRAT/HMAT tables. Firmware tables are persistent boot inputs; kernel maps are runtime-only and may be invalidated if table checks fail.

## Dependencies and integration points
It depends on Linux NUMA definitions when enabled and integrates ACPI SRAT/HMAT parsing with memory topology, CPU/node affinity, device locality, and heterogeneous memory attributes. It is used by architecture-specific ACPI boot paths and memory-management code.

## Risks and test signals
Risks include exceeding PXM domain limits, firmware SRAT revisions changing semantics, stale node/PXM maps after validation failure, disabled stubs silently collapsing all PXMs to node 0, and HMAT remaining enabled after SRAT rejection. Test signals include SRAT systems with PXM values above 255, invalid SRAT fallback, node-to-PXM round trips, `fix_pxm_node_maps()` after sparse node assignment, HMAT disable behavior, and `CONFIG_ACPI_NUMA=n` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h

## Purpose
`acpiosxf.h` declares the ACPICA OS Services Layer (OSL): the callbacks and services the host OS must provide so the OS-independent ACPICA core can initialize, map tables, allocate memory, synchronize, schedule work, access I/O and PCI config space, install interrupts, print diagnostics, and interact with debugger/table-provider facilities.

## Important APIs, types, and functions
Important types and constants include `acpi_execute_type`, `ACPI_NO_UNIT_LIMIT`, `ACPI_MUTEX_SEM`, `ACPI_SIGNAL_FATAL`, `ACPI_SIGNAL_BREAKPOINT`, and `struct acpi_signal_fatal_info`. Function groups include initialization (`acpi_os_initialize`, `acpi_os_terminate`), table override/discovery, spinlocks and raw spinlocks, semaphores, mutexes, allocation and cache APIs, physical memory mapping, interrupt handler install/remove, thread/work execution (`acpi_os_execute`, `acpi_os_wait_events_complete`), sleep/stall, port/memory/PCI access, pointer readability/writability, timers, sleep entry, formatted output, debugger command hooks, trace points, table lookup by name/index/address, and directory iteration for tools.

## Control flow
ACPICA calls into these functions whenever it needs host services. Initialization asks the OS for the root pointer and table overrides, table management maps/unmaps physical memory, event code installs interrupt handlers and schedules notify/GPE work, interpreter synchronization uses OSL locks/semaphores/mutexes, and hardware access paths use OSL port/memory/PCI functions. `ACPI_USE_ALTERNATE_PROTOTYPE_*` allows an environment to substitute prototypes.

## State and persistence behavior
This header owns no state, but OSL implementations maintain locks, caches, mappings, scheduled work, interrupt registrations, and output destinations. Table overrides may redirect persistent firmware inputs to OS-provided replacement tables for the current boot.

## Dependencies and integration points
It depends on ACPICA platform environment and types. In Linux, implementation lives in ACPI OSL code and bridges ACPICA to kernel allocators, spinlocks, workqueues, IRQ APIs, ioremap, PCI config access, printk/debugging, and firmware table override mechanisms.

## Risks and test signals
Risks include deadlocks from wrong lock semantics, sleeping in atomic paths, mismatched map/unmap lifetimes, incorrect access widths, PCI config failures, interrupt removal races, workqueue draining issues, table override lifetime bugs, and debugger hooks compiled into unsuitable environments. Test signals include ACPICA initialization/termination, table override tests, lock/semaphore timeout behavior, GPE/notify work execution, memory and I/O operation-region access, PCI config region access, sleep/stall timing, interrupt install/remove stress, and builds with alternate prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpixf.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpixf.h

## Purpose
`acpixf.h` defines ACPICA's public external interface, runtime configuration globals, feature-dependent stub macros, and the exported function prototypes for initialization, table management, namespace traversal, object evaluation, handlers, events, resources, hardware registers, sleep, timers, diagnostics, and debugger support.

## Important APIs, types, and functions
It declares `ACPI_CA_VERSION` and global configuration variables such as `acpi_gbl_enable_interpreter_slack`, `acpi_gbl_auto_serialize_methods`, `acpi_gbl_create_osi_method`, `acpi_gbl_enable_table_validation`, `acpi_gbl_copy_dsdt_locally`, `acpi_gbl_do_not_use_xsdt`, FADT address policy flags, `acpi_gbl_reduced_hardware`, `acpi_gbl_use_global_lock`, `acpi_gbl_max_loop_iterations`, trace globals, debug masks, `acpi_gbl_FADT`, and `acpi_current_gpe_count`. Public APIs include subsystem initialization, ACPI enable/disable, system info/statistics, interface management, table install/load/unload/get/put, namespace walking, handle/name/data APIs, object evaluation, method installation, notify/address-space/exception/interface handlers, global lock and AML mutexes, fixed events, GPEs, resource conversion/walking, reset and GAS read/write, sleep/wake, PM timer, diagnostic print functions, debug trace functions, and Linux-specific divergence `acpi_get_data_full()`.

## Control flow
A typical boot flow calls table initialization, subsystem initialization, ACPI enablement, table loading, and object initialization. Drivers then query tables, walk namespace nodes, evaluate methods, install notify or address-space handlers, and manage GPE/fixed events. Hardware-dependent APIs are compiled into stubs returning `AE_NOT_CONFIGURED`, `AE_OK`, or zero when `ACPI_REDUCED_HARDWARE` is true; diagnostic/debug/application/debugger APIs are similarly stubbed based on build flags.

## State and persistence behavior
This header declares the global runtime policy knobs and core table state but does not implement storage unless `DEFINE_ACPI_GLOBALS` is set. Runtime state includes table descriptors, FADT copy, GPE counts, debug settings, OSI/interface state, and interpreter behavior flags. Firmware tables remain persistent inputs; ACPICA state is rebuilt each boot and destroyed by `acpi_terminate()`.

## Dependencies and integration points
It includes `acconfig.h`, `actypes.h`, `actbl.h`, and `acbuffer.h`, and is included by `acpi.h`. Linux ACPI bus, drivers, OSL, resource, PM, and hardware code all depend on these declarations. It is the main ABI surface between ACPICA core and its consumers.

## Risks and test signals
Risks include global policy flags being changed after initialization, reduced-hardware stubs hiding missing behavior, table reference leaks due to unmatched `acpi_get_table()`/`acpi_put_table()`, GPE handler ordering mistakes, address-space handler `_REG` sequencing, sleep-state register misuse, debug macros compiled inconsistently, and public ABI drift. Test signals include full ACPICA boot/shutdown, table load/unload and reference counting, namespace walk/evaluate paths, handler install/remove races, GPE enable/disable/wake masks, resource conversion, GAS read/write, sleep/resume, and builds with reduced hardware, no error messages, debug output, debugger, and application flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpixf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acrestyp.h -->
# sources/distributed-fs/ceph-client/include/acpi/acrestyp.h

## Purpose
`acrestyp.h` defines ACPICA's in-memory resource descriptor ABI for ACPI resource templates such as `_CRS`, `_PRS`, `_SRS`, `_AEI`, and PCI routing tables. It maps AML resource descriptors into typed C structures for IRQs, DMA, I/O, memory, address spaces, GPIO, serial buses, pin controls, clocks, vendor data, and routing entries.

## Important APIs, types, and functions
Important base types are `acpi_rs_length`, `acpi_rsdesc_size`, `struct acpi_resource`, `union acpi_resource_data`, `struct acpi_pci_routing_table`, and `ACPI_NEXT_RESOURCE()`. Descriptor structures cover small and large resources: IRQ, DMA, dependent-function markers, I/O/fixed I/O, fixed DMA, vendor and typed vendor data, memory24/32/fixed memory32, address16/32/64, extended address64, extended IRQ, generic register, GPIO, I2C/SPI/UART/CSI2 serial bus, pin function/config/group descriptors, and clock input. Constants encode resource type IDs, memory cache/write attributes, interrupt trigger/polarity/share/wake attributes, DMA width, address decode and producer/consumer roles, serial bus modes, UART settings, pin config values, and resource sizing.

## Control flow
This header has no implementation, but ACPICA resource conversion code uses these structures when turning AML byte streams into linked `struct acpi_resource` buffers. Callers walk a returned buffer by advancing with `ACPI_NEXT_RESOURCE()` until `ACPI_RESOURCE_TYPE_END_TAG`. Resource walkers in `acpixf.h` pass each descriptor to caller callbacks.

## State and persistence behavior
Resource buffers are transient caller-owned allocations returned from ACPICA APIs. Persistent resource definitions live in firmware AML. Pointer fields in variable-length descriptors reference data inside generated buffers or separately managed allocations depending on conversion code.

## Dependencies and integration points
It depends on ACPICA packing, flexible-array, UUID, alignment, and pointer-arithmetic helpers. Linux ACPI resource parsing, platform-device creation, GPIO/I2C/SPI/UART enumeration, pinctrl setup, PCI IRQ routing, and operation-region setup all consume these descriptors.

## Risks and test signals
Risks include structure packing/alignment drift from AML layout, incorrect `length` fields causing resource-walk overruns, variable-length pointer lifetime bugs, unsupported new resource type IDs, endian/width errors in address descriptors, malformed firmware with missing end tags, and ambiguity between similar pin/GPIO/serial fields. Test signals include parsing `_CRS` with every descriptor family, malformed resource templates, extended IRQ and PCI routing tables, serial bus descriptors for I2C/SPI/UART/CSI2, pin group descriptors, `ACPI_NEXT_RESOURCE()` bounds checks, and conversion to address64 resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acrestyp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl.h

## Purpose
`actbl.h` defines the fundamental ACPI table structures directly consumed by ACPICA: common ACPI table headers, Generic Address Structures, RSDP/RSDT/XSDT, FACS, FADT, table descriptors, table-origin flags, FADT size/version helpers, and signature constants. It also includes the additional table catalogs from `actbl1.h`, `actbl2.h`, and `actbl3.h`.

## Important APIs, types, and functions
Important signatures include `ACPI_SIG_DSDT`, `ACPI_SIG_FADT`, `ACPI_SIG_FACS`, `ACPI_SIG_RSDP`, `ACPI_SIG_RSDT`, `ACPI_SIG_XSDT`, and `ACPI_SIG_SSDT`. Core structures are `struct acpi_table_header`, `struct acpi_generic_address`, `struct acpi_table_rsdp`, `struct acpi_rsdp_common`, `struct acpi_rsdp_extension`, `struct acpi_table_rsdt`, `struct acpi_table_xsdt`, `struct acpi_table_facs`, `struct acpi_table_fadt`, `union acpi_name_union`, and `struct acpi_table_desc`. Flags define FACS global-lock/wake behavior, FADT boot architecture and hardware flags, preferred PM profiles, sleep-control bits, table origins, verification/loading state, validation limits, and FADT version sizes.

## Control flow
There is no local runtime flow, but ACPICA table discovery uses the RSDP and RSDT/XSDT structures to locate other tables; FADT parsing populates `acpi_gbl_FADT` and drives hardware availability, SCI/GPE block setup, reset, sleep, and reduced-hardware decisions; FACS fields support global lock and waking vectors. The table manager tracks mapped/loaded tables through `struct acpi_table_desc`.

## State and persistence behavior
ACPI tables are firmware-provided persistent boot data, typically mapped into kernel memory. `struct acpi_table_desc` is runtime state tracking address, pointer, length, signature, owner ID, flags, and validation count. FADT/FACS fields describe firmware/platform state and may be copied, mapped, or overridden for the boot.

## Dependencies and integration points
`acpixf.h`, OSL table functions, Linux ACPI boot, PM, reset, event, and table override code all use these structures. GAS definitions also integrate with `acpi_io.h`, `acpiosxf.h`, and ACPICA register access APIs.

## Risks and test signals
Risks include byte-packing violations, misaligned 64-bit GAS accesses, trusting revision instead of length, corrupt 64-bit versus 32-bit FADT addresses, table validation leaks due to unmatched get/put, malformed checksums, and reduced-hardware flag handling. Test signals include RSDP discovery, RSDT versus XSDT fallback, FADT length variants V1/V2/V3/V5/V6, FACS global-lock behavior, sleep/reset register access, table override/install/unload, and checksum/length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl1.h -->
# sources/distributed-fs/ceph-client/include/acpi/actbl1.h

## Purpose
`actbl1.h` defines many additional ACPI table layouts used primarily by OS drivers, firmware error handling, debug/boot infrastructure, IOMMU/NUMA/memory-topology code, CXL support, and ACPICA disassembly tools. These tables are not all consumed directly by ACPICA core, but they form the shared binary ABI between firmware and Linux ACPI subsystems.

## Important APIs, types, and functions
The header declares signatures for tables including AEST, ASF, ASPT, BERT, BGRT, BOOT, CDAT, CEDT, CPEP, CSRT, DBG2, DBGP, DMAR, DRTM, DTPR, ECDT, EINJ, ERST, FPDT, GTDT, HEST, HMAT, HPET, IBFT, MSCT, NBFT, PCCS, S3PT, and reserved/field-seen signatures. Common structures include `struct acpi_subtable_header`, `struct acpi_subtbl_hdr_16`, and `struct acpi_whea_header`. Major table families include ASF remote-management records, BERT/HEST generic error records, CXL CDAT/CEDT structures, CSRT resources, debug-port tables, Intel DMAR subtables and device scopes, DRTM and DTPR security/protection structures with bit helper macros, ECDT boot EC resources, EINJ/ERST WHEA action entries, FPDT/S3PT performance records, ARM GTDT timers/watchdogs, HMAT heterogeneous memory locality/cache records, HPET timers, and iBFT boot network records.

## Control flow
This header is declarative. Runtime parsers locate a table by signature, validate the common header and length, then walk variable-length subtables using the family-specific header length fields. WHEA-style tables execute action/instruction entries against GAS registers. DMAR, CEDT, HMAT, GTDT, HPET, and iBFT consumers translate table data into kernel subsystems such as IOMMU, CXL, NUMA/memory tiers, timers, watchdogs, and boot networking.

## State and persistence behavior
The structures describe firmware-persistent boot tables and sometimes firmware-owned memory regions. Runtime state is created by consumers after parsing, such as IOMMU units, error-source records, timer devices, EC boot resources, memory-locality data, or CXL windows. The header owns no mutable state.

## Dependencies and integration points
It depends on packed ACPI table layout conventions and `struct acpi_generic_address` from `actbl.h`. Integration points span Linux APEI/WHEA error handling, CXL, VT-d/IOMMU, trusted execution, EC, debug console discovery, HPET/ARM timer drivers, NUMA/HMAT memory topology, iSCSI boot, and platform boot graphics/performance reporting.

## Risks and test signals
Risks include walking malformed variable-length subtables, using stale spec revisions, structure-size drift, flexible-array bounds errors, action-table instruction misuse, security-sensitive table trust in DRTM/DTPR/DMAR, and consumer disagreement on flags or address widths. Test signals include table checksum and length fuzzing, subtable length underflow/overflow tests, DMAR device-scope parsing, EINJ/ERST action execution with preserve masks, HEST/BERT generic error data parsing, CEDT/CDAT/HMAT topology parsing, GTDT timer/watchdog discovery, ECDT EC boot setup, HPET discovery, iBFT parsing, and build coverage for all table consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/actbl1.h -->
