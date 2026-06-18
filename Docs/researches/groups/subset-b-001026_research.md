# Research: subset-b-001026

This grouped report covers ACPI PCI routing/root discovery, platform firmware runtime update/telemetry, platform profile sysfs, ACPI PMIC operation regions, power resources, PPTT topology, PRMT runtime services, and legacy wakeup proc support under `sources/distributed-fs/ceph-client/drivers/acpi`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c

## Purpose
`pci_link.c` implements the ACPI PCI Interrupt Link Device handler for `PNP0C0F` objects. It discovers possible/current legacy interrupt routes from `_PRS` and `_CRS`, programs a selected IRQ through `_SRS`, disables unused links with `_DIS`, and exposes allocation/free helpers used by ACPI PCI IRQ routing.

## Important APIs, Types, and Functions
The main state types are `struct acpi_pci_link_irq`, which caches active IRQ, trigger, polarity, resource type, possible IRQs, and initialization state, and `struct acpi_pci_link`, which binds that IRQ state to an ACPI device and reference count. Key functions are `acpi_pci_link_get_possible()`, `acpi_pci_link_get_current()`, `acpi_pci_link_set()`, `acpi_pci_link_allocate_irq()`, `acpi_pci_link_free_irq()`, `acpi_irq_penalty_init()`, `acpi_penalize_isa_irq()`, `acpi_isa_irq_available()`, `acpi_penalize_sci_irq()`, and `acpi_pci_link_init()`.

## Control Flow and State
During ACPI scan attach, `acpi_pci_link_add()` allocates link state, walks `_PRS` for IRQ or extended IRQ descriptors, reads `_CRS`, logs the current route, adds the link to `acpi_link_list`, and disables the link until used. Allocation validates the requested index, locks `acpi_link_lock`, picks the active IRQ if it is valid or chooses the lowest-penalty possible IRQ, calls `_SRS`, verifies or overrides `_CRS`, marks the link initialized, increments `refcnt`, and returns trigger/polarity/name/GSI. Resume iterates all links and reprograms initialized referenced links.

## State and Persistence
Persistent state is the global link list, per-link cached IRQ assignment, reference counts, IRQ penalty table, SCI penalty, and `acpi_irq_balance` boot policy. Hardware/firmware state persists in ACPI link device routing after `_SRS`; the driver deliberately keeps cached assignment state even if a link is later disabled.

## Dependencies and Integration Points
The file depends on ACPI resource walking/evaluation, ACPI scan handlers, PCI IRQ routing, system core resume callbacks, boot parameters, and global ACPI IRQ mode flags. It integrates with PNP/ISA IRQ reservation through penalty helpers and with the ACPI PCI routing code that resolves link devices to GSIs.

## Risks and Test Signals
Risks include only supporting one IRQ resource entry per link, firmware returning `_CRS` values outside `_PRS`, global penalty heuristics misrouting shared legacy IRQs, possible refcount underuse because decrement code is disabled under `FUTURE_USE`, and resume assumptions that cached routes remain valid. Test signals are link enumeration logs, correct `acpi_irq_isa=`/`acpi_irq_pci=` behavior, successful PCI device interrupt delivery in PIC and IOAPIC modes, suspend/resume with legacy INTx devices, and no selection of SCI or always-reserved ISA IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c

## Purpose
`pci_mcfg.c` parses the ACPI MCFG table and provides ECAM configuration-space resources for ACPI PCI roots. It also applies platform-specific quirks that replace generic ECAM operations or fabricate corrected config-space resource ranges for hardware whose MCFG description is incomplete or nonstandard.

## Important APIs, Types, and Functions
`struct mcfg_entry` stores parsed base address, segment, and bus range. With `CONFIG_PCI_QUIRKS`, `struct mcfg_fixup` matches OEM ID/table/revision, segment, and bus range to a `pci_ecam_ops` implementation and optional resource override. Public entry points are `pci_mcfg_lookup()` and `pci_mmcfg_late_init()`. Internal helpers include `pci_mcfg_parse()`, `pci_mcfg_apply_quirks()`, and `pci_mcfg_quirk_matches()`.

## Control Flow and State
Late init calls `acpi_table_parse()` for `MCFG`. The parser validates table length, allocates an array of entries, copies each allocation's segment/address/start/end bus values into `pci_mcfg_list`, and stores OEM identifiers for quirk matching. `pci_mcfg_lookup()` first honors root `_CBA` if present, otherwise searches parsed MCFG entries that cover the root's segment and bus resource. It builds a memory resource from base plus bus offset, applies quirks, rejects missing starts, and returns the final resource and ECAM ops.

## State and Persistence
The parsed `pci_mcfg_list` and saved OEM fields remain for the lifetime of the kernel. Per-root lookup may cache `root->mcfg_addr`. No userspace persistence exists; the state is boot firmware table interpretation.

## Dependencies and Integration Points
The file depends on ACPI table parsing, `struct acpi_pci_root`, PCI ECAM APIs, architecture-specific ECAM ops, resource helpers, and config-specific quirk tables for ARM64 and LoongArch. It feeds host-bridge creation paths that need a config-space resource.

## Risks and Test Signals
Risks include memory retained intentionally after init, quirks matching exact padded OEM strings/revisions, bus-range containment rejecting partial coverage, and incorrect fabricated resources causing config-space access faults. Test signals are MCFG detection logs, successful PCI config reads on quirked platforms such as ThunderX, X-Gene, Altra, Tegra194, Graviton, QDF2432, Loongson, and clean failure with `-ENXIO` when no valid ECAM base exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c

## Purpose
`pci_root.c` is the ACPI PCI root bridge scan handler. It recognizes root bridge devices, derives domain and bus ranges, negotiates PCIe/CXL `_OSC` ownership, scans PCI buses, manages hot-add/remove, and provides reusable helpers for ACPI-backed root-bus resource probing and creation.

## Important APIs, Types, and Functions
Public helpers include `acpi_is_root_bridge()`, `acpi_pci_find_root()`, `acpi_get_pci_dev()`, `acpi_pci_probe_root_resources()`, `acpi_pci_root_create()`, and `acpi_pci_root_init()`. Internals include `_OSC` decoding and negotiation helpers, `calculate_support()`, `calculate_control()`, CXL support/control calculators, `acpi_pci_root_add()`, `acpi_pci_root_remove()`, resource validation/remapping helpers, and host-bridge release callbacks.

## Control Flow and State
The scan handler attaches to `PNP0A03` root bridges. Attach reads `_SEG`, reads bus number range from `_CRS` or falls back to `_BBN`/0, marks bridge type from HID (`PNP0A08` for PCIe, `ACPI0016` for CXL), obtains `_CBA`, negotiates `_OSC`, scans the root with `pci_acpi_scan_root()`, optionally disables ASPM, installs ACPI PM notifiers, handles hot-add resource assignment/IOAPIC discovery, and adds devices under rescan/remove locking. Remove stops and removes the root bus, tears down IOAPIC/DMAR/PM notifier state, and frees root data. `acpi_pci_root_create()` prepares resources, inserts host-bridge windows, creates the root bus, applies native-service flags from `_OSC`, powers up children with `_ADR`, scans, and records release data.

## State and Persistence
Per-root `struct acpi_pci_root` stores segment, bus range, MCFG address, bridge type, bus pointer, and granted `_OSC` control masks. Resource windows are inserted into global I/O and memory resource trees until host-bridge release. ACPI root device `driver_data` ties firmware nodes to PCI root state.

## Dependencies and Integration Points
Dependencies include ACPI scan/hotplug, PCI core, PCIe ASPM/AER/DPC/EDR/hotplug capabilities, CXL `_OSC`, DMAR, IOAPIC hotplug, architecture root scanning via `pci_acpi_scan_root()`, CRS quirks, and ACPI power/PM notifier code. `acpi_get_pci_dev()` bridges ACPI physical-node links to PCI device references.

## Risks and Test Signals
Risks include firmware missing `_CRS` bus ranges, `_OSC` fallback changing CXL roots to PCIe mode, Apple `_OSC` special-casing, native service flags being wrong if control masks are stale, resource-window overlap pruning, and hot-remove ordering around PCI/IOAPIC/DMAR. Test signals include root bridge logs, correct domain:bus ranges, `_OSC` granted/retained messages, PCI enumeration under boot and hot-add, ASPM behavior when FADT forbids it, CXL error-control negotiation, and clean hot-remove without resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c

## Purpose
`pci_slot.c` creates Linux `pci_slot` objects from ACPI slot metadata below a PCI bus bridge. It finds ACPI device children with `_ADR` and `_SUN`, names slots by the slot user number, and removes those slot objects when the bus is removed.

## Important APIs, Types, and Functions
`struct acpi_pci_slot` links a `struct pci_slot` into the module-global slot list. Public functions are `acpi_pci_slot_enumerate()`, `acpi_pci_slot_remove()`, and `acpi_pci_slot_init()`. Internal helpers are `check_slot()`, `register_slot()`, and the DMI callback `do_sta_before_sun()`.

## Control Flow and State
Enumeration obtains the ACPI handle for `bus->bridge`, locks `slot_list_lock`, and walks one ACPI namespace level below the bridge. `check_slot()` optionally evaluates `_STA` first on quirked systems, reads `_ADR` to obtain the PCI device number, and requires `_SUN` to identify a real slot. `register_slot()` skips duplicate bus/device slots, allocates wrapper state, calls `pci_create_slot()`, appends it to `slot_list`, and holds a reference on the PCI bus device. Removal walks the global list, destroys slots for the removed bus, drops bus references, and frees wrappers.

## State and Persistence
Persistent state is the global `slot_list`, each created `pci_slot`, and the `check_sta_before_sun` DMI quirk flag. There is no stored firmware state; slot objects reflect current ACPI namespace and PCI bus lifetime.

## Dependencies and Integration Points
The file depends on ACPI namespace walking, `_ADR`, `_SUN`, optional `_STA`, PCI slot core APIs, DMI matching, and PCI bus bridge ACPI handles. It is called by PCI/ACPI bus setup and teardown.

## Risks and Test Signals
Risks include ignoring allocation failure during namespace walk, duplicate suppression only by bus/device, `_SUN` side effects on absent Fujitsu PRIMEQUEST slots unless the DMI quirk fires, and slot names limited to numeric strings. Test signals are `/sys/bus/pci/slots` entries with expected names, no duplicate slots for multifunction devices, correct behavior on Fujitsu PRIMEQUEST firmware, and slot cleanup when a hot-added root bus is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c

## Purpose
`pfr_telemetry.c` exposes the ACPI Platform Firmware Runtime Telemetry interface for devices matching `INTC1081`. It lets userspace configure firmware log level/type, query log buffer metadata through `_DSM`, and mmap the firmware telemetry buffer read-only.

## Important APIs, Types, and Functions
`struct pfrt_log_device` stores IDA index, current `struct pfrt_log_info`, parent device, and miscdevice. Important helpers are `get_pfrt_log_data_info()`, `set_pfrt_log_level()`, `get_pfrt_log_level()`, validators for log level/type/revision, `pfrt_log_ioctl()`, `pfrt_log_mmap()`, and probe/remove functions. The UAPI is `PFRT_LOG_IOC_SET_INFO`, `PFRT_LOG_IOC_GET_INFO`, and `PFRT_LOG_IOC_GET_DATA_INFO` from `<uapi/linux/pfrut.h>`.

## Control Flow and State
Probe verifies an ACPI handle and `_DSM`, allocates an ID, initializes revision 1, registers a dynamic miscdevice named `pfrtN` with node `acpi_pfr_telemetryN`, and stores driver data. Ioctls copy UAPI structs, validate revision/level/type, call `_DSM` functions 1, 2, or 3 with typed package results, and copy results back. `mmap()` rejects writable mappings, clears `VM_MAYWRITE`, queries log data, uses chunk2 physical address as base, validates page alignment and mapping size, marks the VMA noncached, and maps it with `io_remap_pfn_range()`.

## State and Persistence
State persists per miscdevice in selected log revision, log type, and cached log level field. Firmware owns the actual telemetry buffer and rollover/reset counters. IDA indices persist for the platform-device lifetime and are freed through devm action.

## Dependencies and Integration Points
The driver depends on ACPI `_DSM` package layouts for the PFRT telemetry GUID, miscdevice/file operations, uaccess, MM remapping, UAPI structs, platform-device ACPI matching, and firmware-provided physical log buffers. It complements `pfr_update.c`, whose update operations create telemetry data.

## Risks and Test Signals
Risks include trusting firmware package buffer sizes after type checks, no explicit serialization across concurrent ioctl/mmap updates to `info`, requiring page-aligned firmware buffer addresses and sizes, using chunk2 as the mmap base, and returning negative log-level errors as a `u32` field to userspace. Test signals are miscdevice creation, `_DSM` status/ext-status debug logs, valid rejection of bad revisions/levels/types, read-only mmap enforcement including `mprotect`, telemetry buffer visibility after a PFRU update, and removal deregistering the miscdevice.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c

## Purpose
`pfr_update.c` implements the ACPI Platform Firmware Runtime Update interface for `INTC1080` devices. It exposes a miscdevice that accepts EFI capsule images, copies them into a firmware communication buffer, verifies basic applicability against firmware capabilities, and starts stage/activate operations through `_DSM`.

## Important APIs, Types, and Functions
`struct pfru_device` stores revision ID, IDA index, parent device, and miscdevice. Core helpers are `query_capability()`, `query_buffer()`, `get_image_type()`, `adjust_efi_size()`, `applicable_image()`, `start_update()`, `pfru_ioctl()`, `pfru_write()`, and platform probe/remove. UAPI commands include `PFRU_IOC_QUERY_CAP`, `PFRU_IOC_SET_REV`, `PFRU_IOC_STAGE`, `PFRU_IOC_ACTIVATE`, and `PFRU_IOC_STAGE_ACTIVATE`.

## Control Flow and State
Probe checks ACPI `_DSM`, allocates an ID, defaults revision to 1, creates miscdevice `pfruN` with node `acpi_pfr_updateN`, and stores device state. `write()` queries the communication buffer, rejects oversize capsules, maps firmware physical memory with `memremap(MEMREMAP_WB)`, copies userspace bytes through an `iov_iter`, queries capability, parses EFI manage-capsule headers, checks image GUID and monotonic runtime/SVN version, unmaps, and returns either an error or the byte count. Ioctls query capability to userspace, set revision after validation, or call `_DSM` start function with stage/activate action and parse update timing/status results.

## State and Persistence
The driver persists only per-device revision/index/miscdevice state. Firmware owns capability state, communication buffer contents, authentication/execution timing, update staging, and activation state. The communication buffer is transiently mapped for each write.

## Dependencies and Integration Points
Dependencies include ACPI `_DSM` package formats for the PFRU GUID, EFI capsule header structures, UAPI `pfrut.h`, miscdevice operations, IDA, uaccess/iov iterators, physical memory mapping, and platform ACPI matching. Telemetry can be observed separately through `pfr_telemetry.c`.

## Risks and Test Signals
Risks include complex capsule pointer arithmetic with limited length validation beyond `len <= buf_size`, package buffer `memcpy()` using firmware-reported lengths into fixed UAPI fields, concurrent writers with no per-device mutex, WB mapping assumptions for firmware memory, and firmware update operations that can be costly or irreversible. Test signals are capability query output, communication buffer query failures, rejection of invalid revision/image GUID/old versions/oversize writes, successful stage/activate `_DSM` status, debug timing logs, and cleanup of miscdevices/IDA indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c

## Purpose
`platform_profile.c` provides the ACPI platform profile sysfs interface. It lets platform drivers register profile handlers, exposes per-handler class devices under `platform-profile`, maintains the legacy aggregate `/sys/firmware/acpi/platform_profile*` attributes, and exports helpers to notify or cycle profiles.

## Important APIs, Types, and Functions
The main private type is `struct platform_profile_handler`, containing handler name, class device, IDA minor, visible/hidden choices bitmaps, and `platform_profile_ops`. Exported APIs are `platform_profile_register()`, `platform_profile_remove()`, `devm_platform_profile_register()`, `platform_profile_notify()`, and `platform_profile_cycle()`. Sysfs helpers include `choices_show`, `profile_show`, `profile_store`, aggregate choice/profile functions, and visibility logic for legacy attributes.

## Control Flow and State
Module init exits if ACPI is disabled, registers the class, and creates the aggregate ACPI sysfs group. Registration validates ops, calls driver `probe()` to fill choices, optionally obtains hidden choices, allocates a minor under `profile_lock`, registers a class device named `platform-profile-N`, notifies the legacy attribute, and updates group visibility. Per-device stores set only that handler after checking visible or hidden support. Legacy stores compute intersection of all registered choices, reject `custom`, set every handler, emit per-handler notifications, and notify the ACPI kobject. `platform_profile_cycle()` aggregates current profile and choices, skips custom/max-power, wraps to the next common profile, and sets all handlers.

## State and Persistence
Persistent runtime state is the class device set, IDA minors, profile choices/hidden choices, and driver-owned current profile state accessed through callbacks. Aggregate sysfs results are computed on demand and disappear when no handlers are registered.

## Dependencies and Integration Points
The file depends on ACPI kobject sysfs, Linux class/device APIs, IDA, mutex/cleanup guard helpers, bitmap operations, `find_next_bit_wrap()`, and `include/linux/platform_profile.h` callback contracts. It integrates with vendor platform drivers that implement `profile_get`, `profile_set`, `probe`, and optional `hidden_choices`.

## Risks and Test Signals
Risks include aggregate legacy semantics requiring all handlers to support a requested profile, hidden choices being allowed for per-device writes but hidden from legacy choices when only one handler exists, callback errors aborting multi-device stores mid-operation, and reliance on drivers returning valid enum values. Test signals are class device attributes `name/choices/profile`, aggregate attributes appearing only with registered handlers, uevents and sysfs notifications on changes, cycle behavior across supported choices, devm cleanup, and concurrent register/remove/store under `profile_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig

## Purpose
`pmic/Kconfig` defines build-time options for ACPI PMIC operation region support. It groups the Intel SoC PMIC opregion core and chip-specific drivers under `PMIC_OPREGION`, while defining TPS68470 support as a separate bool because it must be available early for devices that consume its opregions.

## Important APIs, Types, and Functions
This file has no runtime functions. Important symbols are `PMIC_OPREGION`, `BYTCRC_PMIC_OPREGION`, `CHTCRC_PMIC_OPREGION`, `XPOWER_PMIC_OPREGION`, `BXT_WC_PMIC_OPREGION`, `CHT_WC_PMIC_OPREGION`, `CHT_DC_TI_PMIC_OPREGION`, and `TPS68470_PMIC_OPREGION`.

## Control Flow and State
Kconfig selection gates compilation. Enabling `PMIC_OPREGION` makes the common Intel `intel_pmic.o` buildable and exposes per-PMIC bool choices. Each child option depends on the relevant MFD/SoC PMIC provider. TPS68470 depends on `INTEL_SKL_INT3472` and stays outside the Intel menu group.

## State and Persistence
The selected symbols persist in the kernel configuration and directly determine which built-in opregion handlers are linked. These are bool options, not modules, so selected drivers are expected to be present during ACPI enumeration.

## Dependencies and Integration Points
Dependencies map each ACPI opregion driver to its MFD provider: `INTEL_SOC_PMIC`, `INTEL_SOC_PMIC_BXTWC`, `INTEL_SOC_PMIC_CHTWC`, `INTEL_SOC_PMIC_CHTDC_TI`, `MFD_AXP20X_I2C` plus built-in `IOSF_MBI`, and `INTEL_SKL_INT3472`. The file integrates with the Makefile in the same directory.

## Risks and Test Signals
Risks include missing opregion handlers if the bool is not selected, probe ordering failures if a provider is modular when an opregion must be built-in, and dependencies becoming stale as MFD driver names change. Test signals are expected object files in built-in kernel builds, ACPI devices no longer deferring on PMIC opregions, and Kconfig dependency checks for x86 tablet and camera platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile

## Purpose
`pmic/Makefile` maps ACPI PMIC opregion Kconfig symbols to the object files that implement common Intel and chip-specific handlers.

## Important APIs, Types, and Functions
There are no runtime APIs. Build targets are `intel_pmic.o`, `intel_pmic_bytcrc.o`, `intel_pmic_chtcrc.o`, `intel_pmic_xpower.o`, `intel_pmic_bxtwc.o`, `intel_pmic_chtwc.o`, `intel_pmic_chtdc_ti.o`, and `tps68470_pmic.o`.

## Control Flow and State
Kbuild adds objects with `obj-$(CONFIG_...)`. The common Intel core is tied to `CONFIG_PMIC_OPREGION`; variant drivers are tied to their individual symbols; TPS68470 is controlled separately.

## State and Persistence
The file affects build artifacts only. Since the associated Kconfig symbols are bools, selected objects are linked into the kernel image rather than built as loadable modules.

## Dependencies and Integration Points
The Makefile integrates directly with `pmic/Kconfig` and the ACPI driver build. Variant objects depend on `intel_pmic.o` when they call `intel_pmic_install_opregion_handler()` or `intel_soc_pmic_exec_mipi_pmic_seq_element()`.

## Risks and Test Signals
Risks are straightforward build coupling: adding a Kconfig symbol without an object mapping leaves support absent, and compiling a variant without the common object would break linkage. Test signals are successful `drivers/acpi/pmic/` builds for each enabled symbol and expected built-in opregion probe logs on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c

## Purpose
`intel_pmic.c` is the common Intel SoC PMIC ACPI operation-region core. It installs address-space handlers for PMIC power, thermal, and raw register opregions, translates ACPI opregion addresses to PMIC regmap accesses through chip-specific tables, applies optional LPAT temperature conversion, and exports a MIPI PMIC sequence helper for display initialization.

## Important APIs, Types, and Functions
Private state is `struct intel_pmic_opregion`, holding a lock, LPAT table, regmap, variant data, and raw register-handler context. Public exports are `intel_pmic_install_opregion_handler()` and `intel_soc_pmic_exec_mipi_pmic_seq_element()`. Key handlers are `intel_pmic_power_handler()`, `intel_pmic_thermal_handler()`, and `intel_pmic_regs_handler()`. Helper paths include `pmic_get_reg_bit()`, `pmic_read_temp()`, `pmic_thermal_aux()`, and `pmic_thermal_pen()`.

## Control Flow and State
Variant probe calls `intel_pmic_install_opregion_handler()` with a parent ACPI handle, regmap, and `intel_pmic_opregion_data`. The core allocates state, initializes LPAT conversion, conditionally installs power and thermal handlers when tables are nonempty, always installs the raw register handler, and records the global opregion pointer. ACPI reads/writes validate 32-bit accesses, resolve opregion address to table entry, lock the opregion, and call variant callbacks. The raw register opregion stages high/low address and value bytes across offsets 1-3, executes read/write at offset 4, and returns read value at offset 3.

## State and Persistence
Persistent state includes installed ACPI handlers, the LPAT conversion table, raw register context bytes, and the global singleton `intel_pmic_opregion` used by MIPI sequence execution. Hardware state persists in PMIC registers changed through regmap.

## Dependencies and Integration Points
The core depends on ACPI address-space handlers, `acpi_lpat`, regmap, Intel SoC PMIC MFD drivers, and chip-specific `intel_pmic_opregion_data` tables. The MIPI helper integrates with display drivers that need PMIC register writes from VBT MIPI sequences.

## Risks and Test Signals
Risks include singleton global state when multiple PMIC opregions exist, no explicit handler removal path in the common installer, raw register context shared across AML accesses, table/address mismatches returning ACPI errors, and variant callbacks determining actual electrical behavior. Test signals are successful handler installation, AML power/thermal reads and writes, LPAT conversion correctness, MIPI sequence writes on DSI panels, and failure unwinding when a later handler install fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h

## Purpose
`intel_pmic.h` defines the shared table and callback contract between the Intel PMIC opregion core and chip-specific PMIC drivers.

## Important APIs, Types, and Functions
`struct pmic_table` maps an ACPI operation-region address to a PMIC register and bit/control field. `struct intel_pmic_opregion_data` supplies variant callbacks for power, thermal raw reads, auxiliary threshold writes, policy reads/writes, MIPI sequence execution, LPAT conversion, power/thermal table pointers and counts, and a generic PMIC I2C address. The header declares `intel_pmic_install_opregion_handler()`.

## Control Flow and State
There is no runtime control flow in the header. At compile time it fixes the ABI used by variant C files to hand operation tables and functions to the common installer.

## State and Persistence
The structures describe static per-chip tables and function pointers. Once a variant passes them to the common core, they persist as opregion dispatch metadata for the PMIC device lifetime.

## Dependencies and Integration Points
The header depends on `acpi_lpat` declarations, `struct regmap`, `struct device`, and ACPI handles through included Linux headers in users. It integrates all Intel PMIC variant files with `intel_pmic.c`.

## Risks and Test Signals
Risks include callback semantic drift, table counts not matching array sizes, bit fields being interpreted differently by variants, and missing callbacks causing `-ENXIO` for AML paths. Test signals are clean builds of every variant, successful callback dispatch from power/thermal opregions, and MIPI helper behavior through either custom callback or generic I2C-address path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c

## Purpose
`intel_pmic_bxtwc.c` implements ACPI PMIC operation-region support for Broxton Whiskey Cove PMICs. It supplies power rail mappings, thermal sensor mappings, ADC conversion logic, auxiliary threshold programming, and policy bit handlers to the common Intel PMIC core.

## Important APIs, Types, and Functions
Static `power_table` maps ACPI power region offsets to voltage rail control registers and enable bits or modes. `thermal_table` maps thermal opregion offsets to ADC/alert registers and policy bits. Variant callbacks are `intel_bxtwc_pmic_get_power()`, `intel_bxtwc_pmic_update_power()`, `intel_bxtwc_pmic_get_raw_temp()`, `intel_bxtwc_pmic_update_aux()`, `intel_bxtwc_pmic_get_policy()`, and `intel_bxtwc_pmic_update_policy()`. Probe registers `intel_bxtwc_pmic_opregion_data`.

## Control Flow and State
The built-in platform driver matches `bxt_wcove_region`. Probe obtains the parent `intel_soc_pmic` regmap and calls the common installer with the parent ACPI handle. Power reads test configured bits; writes update the bit/mask to all ones or zero. Raw temperature reads low and high ADC bytes, extracts current source, scales by an `rlsb_array`, and returns an ADC-derived raw value. Auxiliary threshold writes compute current select and threshold fields and program high/low alert registers. Policy callbacks read or write individual bits.

## State and Persistence
Persistent state is the static mapping tables and installed handlers. PMIC register changes persist in hardware until changed by firmware, AML, or drivers. No per-variant dynamic state is kept beyond common opregion data.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC MFD parent, regmap, common Intel PMIC opregion core, ACPI LPAT conversion, and the platform-device ID created for Broxton Whiskey Cove regions.

## Risks and Test Signals
Risks include ADC current-source index assumptions, threshold math edge cases for low raw values, enable semantics differing between VR modes and switch bits, and register map differences across PMIC revisions. Test signals are handler probe on `bxt_wcove_region`, AML power rail toggles, thermal readings matching LPAT-scaled sensors, DPTF policy bit writes, and no regmap I/O errors during suspend/resume thermal polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bxtwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c

## Purpose
`intel_pmic_bytcrc.c` implements ACPI operation-region support for Bay Trail Crystal Cove PMICs. It maps ACPI-defined power and thermal offsets to Crystal Cove registers and provides callbacks for rail control, raw temperature access, auxiliary thresholds, and thermal policy enable bits.

## Important APIs, Types, and Functions
The static `power_table` covers known Bay Trail rails, while `thermal_table` covers temperature and auxiliary/policy offsets. Variant callbacks are `intel_crc_pmic_get_power()`, `intel_crc_pmic_update_power()`, `intel_crc_pmic_get_raw_temp()`, `intel_crc_pmic_update_aux()`, `intel_crc_pmic_get_policy()`, and `intel_crc_pmic_update_policy()`. The registered data also sets `.pmic_i2c_address = 0x6e` for generic MIPI PMIC sequence execution.

## Control Flow and State
The built-in platform driver probes under `byt_crystal_cove_pmic`, obtains the parent `intel_soc_pmic` regmap, and installs common handlers. Power reads require both `PWR_SOURCE_SELECT` and the target bit. Power writes preserve source selection and set or clear the target bit. Raw temperature reads a 10-bit value split across register and preceding register. Auxiliary writes update low and high bits. Policy writes temporarily unlock `PMIC_A0LOCK_REG`, update bit 7, and restore the lock register.

## State and Persistence
Static mapping tables and callback data persist in the kernel image. PMIC rail, threshold, and policy settings persist in device registers. The A0 lock register is saved and restored around policy updates.

## Dependencies and Integration Points
The file depends on the Intel SoC PMIC MFD parent, regmap, common Intel PMIC core, LPAT conversion, and MIPI sequence users that address PMIC I2C `0x6e`.

## Risks and Test Signals
Risks include incomplete power table entries for unknown rails, lock-register restore failure leaving policy writes exposed, raw temperature split-register assumptions, and generic MIPI writes being allowed only for the configured I2C address. Test signals are successful probe, AML reads/writes of known rails, thermal/DPTF threshold updates, A0 lock restoration, display panel MIPI PMIC sequence success, and regmap error propagation to ACPI errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_bytcrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c

## Purpose
`intel_pmic_chtcrc.c` provides minimal Cherry Trail Crystal Cove PMIC opregion support. Its main purpose is to register with the common Intel PMIC core so `intel_soc_pmic_exec_mipi_pmic_seq_element()` can execute display PMIC register writes on CHT Crystal Cove systems.

## Important APIs, Types, and Functions
The only variant data is `intel_chtcrc_pmic_opregion_data`, which supplies LPAT conversion and `.pmic_i2c_address = 0x6e` but no power or thermal tables. `intel_chtcrc_pmic_opregion_probe()` installs the common handlers. The built-in platform driver is named `cht_crystal_cove_pmic`.

## Control Flow and State
Probe obtains the parent `intel_soc_pmic` regmap and calls `intel_pmic_install_opregion_handler()` with the parent ACPI handle. Because table counts are zero, the common installer skips power and thermal handlers and installs only the raw register opregion, while the global common opregion pointer enables generic MIPI sequence writes for I2C address `0x6e`.

## State and Persistence
There is no chip-specific dynamic state. The installed raw register handler and global common PMIC opregion state persist for the platform-device lifetime.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC parent, regmap, common Intel PMIC opregion core, and display/VBT users of the exported MIPI PMIC sequence helper.

## Risks and Test Signals
Risks include lack of documented power/thermal support, so AML expecting those opregions would fail, and reliance on generic MIPI register writes matching the PMIC address. Test signals are successful probe, no attempted DPTF thermal opregion access on unsupported systems, and working DSI panel initialization through PMIC sequence elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtcrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c

## Purpose
`intel_pmic_chtdc_ti.c` supports ACPI operation regions for Cherry Trail Dollar Cove TI PMICs. It maps LDO power resources and thermal ADC readings to PMIC registers and registers those mappings with the common Intel PMIC core.

## Important APIs, Types, and Functions
`chtdc_ti_power_table` maps LDO offsets to enable registers. `chtdc_ti_thermal_table` maps thermal offsets to GPADC, BPTHERM, and DIETEMP registers. Callbacks are `chtdc_ti_pmic_get_power()`, `chtdc_ti_pmic_update_power()`, and `chtdc_ti_pmic_get_raw_temp()`. Probe uses `chtdc_ti_pmic_opregion_data` and platform ID `chtdc_ti_region`.

## Control Flow and State
The platform driver obtains the parent `intel_soc_pmic` regmap and installs common opregion handlers. Power reads return bit 0 from each LDO register; writes update bit 0. Raw temperature reads a big-endian 16-bit register pair and masks it to a 10-bit value. After successful handler installation, probe clears ACPI dependencies for the PMIC companion so devices blocked on the opregion can be re-enumerated.

## State and Persistence
Static tables and installed handlers persist for the device lifetime. Power and thermal state lives in PMIC registers. Clearing ACPI dependencies changes enumeration state for devices that waited for the PMIC.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC CHTDC TI MFD parent, regmap bulk reads, byte-order conversion, ACPI dependency handling, LPAT conversion, and the common Intel PMIC core.

## Risks and Test Signals
Risks include assuming all power resources are bit 0, 10-bit big-endian temperature layout, dependency clearing after partial platform setup, and missing auxiliary/policy callbacks for AML paths that might request them. Test signals are successful probe on `chtdc_ti_region`, dependent ACPI devices continuing enumeration, LDO toggles through AML, plausible LPAT-scaled thermal readings, and regmap bulk-read errors surfacing as ACPI failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtdc_ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c

## Purpose
`intel_pmic_chtwc.c` implements ACPI operation-region support for Cherry Trail Whiskey Cove PMICs. It provides regulator/rail power mappings and a custom MIPI PMIC sequence handler for the 16-bit address format used by this PMIC family.

## Important APIs, Types, and Functions
The file defines many Whiskey Cove register constants, a `power_table` for rails such as V18A, V18X, VDDQ, VSDIO, and VPROG rails, callbacks `intel_cht_wc_pmic_get_power()`, `intel_cht_wc_pmic_update_power()`, and `intel_cht_wc_exec_mipi_pmic_seq_element()`, plus platform probe using `intel_cht_wc_pmic_opregion_data`.

## Control Flow and State
The built-in driver matches `cht_wcove_region`, gets the parent PMIC regmap, and installs common handlers. Power reads test a configured bitmask; writes call `regmap_update_bits()` with either 1 or 0. MIPI sequence execution validates 8-bit I2C client and register addresses, composes a regmap address as `(client << 8) | reg`, and updates masked bits. Thermal table/count are intentionally empty because DPTF thermal support lacks documentation.

## State and Persistence
State is static tables and installed handlers. PMIC register writes persist in hardware. No dynamic per-variant state is maintained.

## Dependencies and Integration Points
The driver depends on the Intel SoC PMIC CHT Whiskey Cove MFD, regmap, common Intel PMIC core, ACPI LPAT declarations, and display drivers that execute MIPI PMIC sequence elements.

## Risks and Test Signals
Risks include using `on ? 1 : 0` with multi-bit masks, incomplete/undocumented rails, no thermal opregion support, and MIPI address-range rejection for firmware sequences that encode wider addresses. Test signals are successful `cht_wcove_region` probe, AML rail toggles for mapped offsets, display panel MIPI sequence writes, and lack of DPTF thermal failures on supported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_chtwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c

## Purpose
`intel_pmic_xpower.c` implements ACPI opregion support for XPower AXP288 PMICs. It maps regulator and thermal ACPI offsets to AXP288 regmap operations, coordinates IOSF P-unit I2C access, provides GPADC temperature reads, handles display MIPI PMIC sequence writes, and installs a dummy GPIO opregion handler for firmware compatibility.

## Important APIs, Types, and Functions
Static `power_table` maps ALD/DLD/ELD/FLD/BUC/GPI1 regulators. `thermal_table` maps TMP0-TMP5 to GPADC. Key callbacks are `intel_xpower_pmic_get_power()`, `intel_xpower_pmic_update_power()`, `intel_xpower_pmic_get_raw_temp()`, `intel_xpower_exec_mipi_pmic_seq_element()`, `intel_xpower_lpat_raw_to_temp()`, and `intel_xpower_pmic_gpio_handler()`. Probe installs both GPIO and PMIC opregion handlers.

## Control Flow and State
Probe gets the parent `axp20x_dev`, installs an ACPI GPIO address-space handler that returns `AE_OK`, then installs common PMIC handlers with AXP288 regmap data. Regulator writes block P-unit I2C access before touching PMIC registers; GPI1 LDO uses a special three-bit on/off encoding. GPADC reads temporarily switch the TS current source to on-demand when needed, waits, blocks P-unit access, bulk reads ADC bytes, restores TS current-source mode, and unblocks access. MIPI sequence writes require I2C address `0x34` and update masked bits under IOSF blocking.

## State and Persistence
Static mappings persist in the kernel. Hardware regulator, TS-current, and PMIC register states persist in the PMIC. The GPIO opregion handler has no state and is installed only to satisfy AML access.

## Dependencies and Integration Points
Dependencies include the AXP20x MFD parent, regmap, IOSF MBI locking, common Intel PMIC core, LPAT conversion, ACPI GPIO address-space handling, and display MIPI sequence users.

## Risks and Test Signals
Risks include failing to restore TS current mode on some error paths, IOSF lock/unlock ordering, special GPI1 LDO encoding, LPAT clamping hiding firmware table range defects, and dummy GPIO handling masking AML expectations. Test signals are successful probe on `axp288_pmic_acpi`, regulator AML toggles without P-unit conflicts, plausible temperature readings with TS current restored, MIPI writes to address `0x34`, and no ACPI GPIO opregion errors during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/intel_pmic_xpower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/tps68470_pmic.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pmic/tps68470_pmic.c

## Purpose
`tps68470_pmic.c` implements ACPI operation-region support for the TI TPS68470 PMIC used by camera-related INT3472 designs. It exposes ACPI regions for power control, regulator voltage values, clock control, and clock frequency programming through a TPS68470 regmap.

## Important APIs, Types, and Functions
`struct tps68470_pmic_table` maps opregion addresses to registers and masks. `struct tps68470_pmic_opregion` stores a lock and regmap. Tables are `power_table`, `vr_val_table`, `clk_freq_table`, and `clk_table`. Core helpers are `pmic_get_reg_bit()`, getter functions for power/voltage/clock/frequency fields, `ti_tps68470_regmap_update_bits()`, `tps68470_pmic_common_handler()`, specific ACPI handlers for each region, and `tps68470_pmic_opregion_probe()`.

## Control Flow and State
Probe obtains the parent regmap and ACPI handle, allocates opregion state, initializes a mutex, and installs four address-space handlers in order: power `0xB0`, voltage value `0xB1`, clock `0xB2`, and clock frequency `0xB3`. Each handler validates 32-bit accesses, maps `address / 4` to a table entry, rejects writes outside the mask, locks, performs read or masked update, unlocks, and returns ACPI status. Failure unwinds previously installed handlers.

## State and Persistence
Persistent state is installed ACPI handlers and the opregion lock/regmap pointer. Actual regulator and clock state persists in TPS68470 registers. There is no remove path because this is a built-in platform driver intended to be present before dependent devices probe.

## Dependencies and Integration Points
The driver depends on the TPS68470 MFD regmap, ACPI address-space handlers, INT3472 platform setup, TPS68470 register definitions, and camera sensor/clock/regulator AML that accesses the PMIC opregions.

## Risks and Test Signals
Risks include assuming opregion addresses are dense four-byte slots, write values must already be positioned within masks, special power writes allowing value 3 only for S-I2C enable bits, and lack of dynamic handler removal. Test signals are successful built-in probe, ACPI camera devices progressing past opregion dependencies, regulator/clock register reads and masked writes, proper unwind when any handler install fails, and camera sensor power-up/clock programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pmic/tps68470_pmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/power.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/power.c

## Purpose
`power.c` manages ACPI Power Resources: firmware objects that represent software-controllable power or clock planes shared by ACPI devices. It extracts power-resource references from device packages, creates ACPI power-resource devices, maintains reference counts, turns resources on/off for device D-state and wake transitions, exposes sysfs links, and handles resume/unused-resource quirks.

## Important APIs, Types, and Functions
Important types are `struct acpi_power_resource`, `struct acpi_power_resource_entry`, and `struct acpi_power_dependent_device`. Public functions include `acpi_extract_power_resources()`, `acpi_power_resources_list_free()`, `acpi_device_power_add_dependent()`, `acpi_device_power_remove_dependent()`, `acpi_power_add_remove_device()`, `acpi_power_wakeup_list_init()`, `acpi_device_sleep_wake()`, `acpi_enable_wakeup_device_power()`, `acpi_disable_wakeup_device_power()`, `acpi_power_get_inferred_state()`, `acpi_power_on_resources()`, `acpi_power_transition()`, `acpi_add_power_resource()`, `acpi_resume_power_resources()`, `acpi_turn_off_unused_power_resources()`, and `acpi_power_resources_init()`.

## Control Flow and State
Power resource extraction validates ACPI reference packages, skips duplicates, creates missing power-resource devices, and inserts entries ordered by firmware resource order. `acpi_add_power_resource()` evaluates the power resource object for system level/order, initializes state from `_STA` or turns it on if state cannot be read, ties and adds the ACPI device, creates `resource_in_use`, and appends it globally. On transitions, the target D-state resources are powered on first, then current-state resources are powered off, preserving power during state changes. Wake enable increments `prepare_count`, powers wake resources, and calls `_DSW` or `_PSW`; wake disable reverses that when the count reaches zero. Resume re-reads resource states and powers on referenced resources that firmware left off, including an HP GP12/PXP off-on quirk.

## State and Persistence
Persistent state includes the global ordered `acpi_power_resource_list`, each resource's cached state, reference count, order/system level, dependent device list, and wake prepare counts in ACPI devices. Firmware methods `_ON`, `_OFF`, `_STA`, `_DSW`, and `_PSW` mutate platform power state. DMI quirk booleans persist after init.

## Dependencies and Integration Points
The file depends on ACPI device core, power-resource package parsing, sysfs, runtime PM, suspend/resume, DMI, ACPI sleep internals, and device power state data in `struct acpi_device`. It integrates with PCI and other bus drivers that add dependents so devices can be runtime-resumed when a shared resource turns back on.

## Risks and Test Signals
Risks include reference-count imbalance leaving rails on/off, firmware `_STA` failures causing forced `_ON`, rollback complexity when list power-on/off partially fails, sysfs link creation failures hiding resource topology, DMI quirk coverage for buggy firmware, and concurrent access requiring the global and per-resource locks. Test signals are correct power resource sysfs groups/links, `resource_in_use` values, D-state transitions preserving dependencies, wake enable/disable counts, suspend/hibernate resume of referenced resources, unused resources turning off except quirked systems, and no inaccessible devices after thaw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pptt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pptt.c

## Purpose
`pptt.c` parses the ACPI Processor Properties Topology Table and uses it to describe CPU topology, cache hierarchy, cache properties, cache IDs, processor containers, package/cluster IDs, and heterogeneous core groupings. It is used by cacheinfo and architecture topology code when firmware supplies PPTT data.

## Important APIs, Types, and Functions
Public functions include `acpi_get_cache_info()`, `cache_setup_acpi()`, `acpi_pptt_cpu_is_thread()`, `find_acpi_cpu_topology()`, `find_acpi_cpu_topology_package()`, `find_acpi_cpu_topology_cluster()`, `find_acpi_cpu_topology_hetero_id()`, `acpi_pptt_get_cpus_from_container()`, `find_acpi_cache_level_from_id()`, and `acpi_pptt_get_cpumask_from_cache_id()`. Key internals are bounds-checked fetch helpers, cache walkers, processor-node search, cache property updates, topology-tag search, and lazy `acpi_get_pptt()`.

## Control Flow and State
The parser lazily maps the PPTT once and intentionally keeps it for runtime CPU hotplug/topology queries. Subtable fetches validate reference offsets, lengths, and table bounds. Processor-node search walks all subtables, matches ACPI processor UID, validates processor entry length including private resource references, and verifies leaf status. Cache queries walk private cache resources and parent processor nodes, count levels, detect split I/D levels, and update cacheinfo fields only when PPTT validity flags are set. Topology helpers walk parent pointers until a requested level, package flag, identical flag, or root is reached. Container/cache-ID helpers iterate possible CPUs and build cpumasks.

## State and Persistence
Persistent state is the cached PPTT table pointer and checked flag. Cacheinfo updates persist in per-CPU cacheinfo structures, including `fw_token`, size/line/sets/associativity/attributes/type/id. No firmware state is modified.

## Dependencies and Integration Points
The file depends on ACPI table structures, ACPI processor UID mapping, Linux cacheinfo, CPU masks, and topology consumers. It integrates with CPU hotplug paths and architectures that ask ACPI for cache and package/cluster/heterogeneity IDs.

## Risks and Test Signals
Risks include malformed relative offsets, zero-length subtables, duplicate cache level/type ambiguity, PPTT revision-dependent semantics for leaf and cache ID fields, CPU UID mismatches, and generated pointer-difference IDs changing with table layout. Test signals are warnings for missing or malformed PPTT, accurate cache level/split counts, cacheinfo overrides matching firmware, package/cluster sibling masks, thread flag detection on revision 2+, cache ID lookup on revision 3+, CPU hotplug topology stability, and fallback behavior when PPTT is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pptt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/prmt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/prmt.c

## Purpose
`prmt.c` initializes ACPI Platform Runtime Mechanism support. It parses the PRMT table, maps firmware PRM handler physical addresses to EFI runtime virtual addresses, records module/handler metadata, exposes handler availability/call helpers, and installs the `PlatformRtMechanism` operation-region handler used by AML to invoke PRM services.

## Important APIs, Types, and Functions
Private packed wire/context types include `prm_mmio_info`, `prm_buffer`, and `prm_context_buffer`. Runtime metadata is `struct prm_module_info` with flexible handler array and `struct prm_handler_info`. Public exports are `acpi_prm_handler_available()` and `acpi_call_prm_handler()`. Key internals are `efi_pa_va_lookup()`, `acpi_parse_prmt()`, GUID lookup helpers, `acpi_platformrt_space_handler()`, and `init_prmt()`.

## Control Flow and State
`init_prmt()` checks for a PRMT table, parses module subtables, logs module count, verifies EFI runtime services, and installs an ACPI root address-space handler for `ACPI_ADR_SPACE_PLATFORM_RT`. Each parsed module allocates metadata, copies module GUID/revisions/count, maps and copies optional MMIO range lists, appends to `prm_module_list`, and converts each handler/static/parameter buffer physical address through EFI runtime descriptors. AML writes a PRM buffer to the opregion handler; `RUN_SERVICE` locates handler/module, builds a PRM context, calls `efi_call_acpi_prm_handler()`, and writes status/EFI status back. Transaction commands toggle the module `updatable` flag. The exported direct call path invokes a handler with a caller-supplied parameter buffer.

## State and Persistence
Persistent state is `prm_module_list`, allocated module/handler metadata, copied MMIO range lists, handler virtual addresses, static/ACPI parameter buffer addresses, and per-module `updatable` flags. PRM services execute in EFI runtime context and may mutate platform firmware/hardware state.

## Dependencies and Integration Points
The file depends on ACPI PRMT structures, EFI runtime memory descriptors, architecture EFI call wrappers, GUID helpers, ACPI operation regions, and exported PRM APIs used by other kernel code. It integrates AML bytecode with EFI PRM service handlers.

## Risks and Test Signals
Risks include physical-to-virtual lookup requiring EFI runtime descriptors that cover handler addresses, memory leaks because PRMT metadata persists permanently, transaction locking not protected by a mutex, continuing after NULL handler addresses inside the parse loop without advancing handler pointers in that iteration, and firmware handler failures reported through buffer fields rather than ACPI status. Test signals are PRMT module count logs, successful opregion handler installation, `acpi_prm_handler_available()` for known GUIDs, AML PRM run-service status values, EFI status propagation, and graceful behavior when EFI runtime services are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/prmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/proc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/proc.c

## Purpose
`proc.c` provides the legacy `/proc/acpi/wakeup` interface. It displays ACPI wake-capable devices, their target sleep state, enable status, and associated physical sysfs devices, and lets userspace toggle wake enablement by writing an ACPI bus ID.

## Important APIs, Types, and Functions
The proc entry uses `acpi_system_wakeup_device_proc_ops`. Important functions are `acpi_system_wakeup_device_seq_show()`, `physical_device_enable_wakeup()`, `acpi_system_write_wakeup_device()`, `acpi_system_wakeup_device_open_fs()`, and `acpi_sleep_proc_init()`.

## Control Flow and State
Init creates `wakeup` under `acpi_root_dir` with mode `0644`. Reads use `single_open()` and iterate `acpi_wakeup_device_list` under `acpi_device_lock`, skipping invalid wake devices. For each ACPI device, output includes bus ID, `S` sleep state, enabled/disabled state, and either no physical node or each linked physical device's bus/name. Writes copy at most four bytes from userspace, parse a bus ID token, lock the wakeup list, find the matching ACPI device, and toggle wakeup on the ACPI device itself if possible or on all wake-capable physical nodes otherwise.

## State and Persistence
The file does not own wake state; it toggles `device_may_wakeup` flags on ACPI or physical devices. The visible list is backed by global ACPI wakeup device registration state.

## Dependencies and Integration Points
Dependencies include procfs, seq_file, ACPI wakeup device lists, device wakeup core APIs, physical-node links, and ACPI sleep initialization. It is a compatibility interface alongside sysfs power/wakeup controls.

## Risks and Test Signals
Risks include four-character bus ID matching via `strncmp()`, writes toggling all physical devices when the ACPI device itself cannot wake, output status combining ACPI and physical wake states, and legacy proc permissions allowing root-driven wake toggles outside sysfs. Test signals are `/proc/acpi/wakeup` formatting, toggling entries by bus ID, matching sysfs `power/wakeup` state changes, correct output for devices with multiple physical nodes, and stable locking while devices are added or removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/proc.c -->
