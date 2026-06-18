# subset-b-001276 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/xgene_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/xgene_edac.c

## Purpose
`xgene_edac.c` is the EDAC platform driver for AppliedMicro/APM X-Gene SoCs. It registers separate EDAC memory-controller and EDAC-device instances for MCU DRAM controllers, PMD CPU/L1/L2 cache blocks, L3 cache blocks, and SoC fabric/IOB errors, then reports corrected and uncorrected hardware errors through the EDAC core in either polling or interrupt mode.

## Important APIs, types, and functions
The root state is `struct xgene_edac`, which owns syscon regmaps, the PCP CSR mapping, shared interrupt masks, debugfs root, child lists, and MCU active/registered masks. Child state is split into `struct xgene_edac_mc_ctx`, `struct xgene_edac_pmd_ctx`, and `struct xgene_edac_dev_ctx`. Key flows are `xgene_edac_probe()`, `xgene_edac_isr()`, `xgene_edac_mc_add()/check()/irq_ctl()`, `xgene_edac_pmd_add()/check()`, `xgene_edac_l3_add()/check()`, and `xgene_edac_soc_add()/check()`. It uses `edac_mc_handle_error()`, `edac_device_handle_ce()`, `edac_device_handle_ue()`, syscon `regmap_read/write`, MMIO `readl/writel`, and optional EDAC debugfs injection handlers.

## Control flow
Module init refuses to load when GHES EDAC devices are present, normalizes `edac_op_state`, and registers a device-tree platform driver for `apm,xgene-edac`. Probe resolves required syscon phandles (`regmap-csw`, `regmap-mcba`, `regmap-mcbb`, `regmap-efuse`), optionally resolves the register-bus regmap, maps PCP CSRs, requests three shared IRQs in interrupt mode, creates debugfs, and iterates child DT nodes. MCU nodes are filtered against active memory-controller topology before `edac_mc_add_mc()`. PMD nodes are filtered using efuse disabled-PMD bits. L3 and SoC nodes become EDAC devices.

At runtime, polling callbacks or the top-level ISR read PCP high/low priority status and MEMERR status, then fan out to registered child checkers. MCU checking walks ranks, reports MCU uncorrectable/correctable rank errors, logs bank/row/column/count for CEs, clears per-rank status, and handles MCU address decode errors. PMD checking decodes CPU ICF/LSU/MMU L1 errors, shared L2 ECC and timeout status, and clears each status register. L3 checking logs syndrome, tag/data, agent, operation, physical address, bank, and promotes known broken version-1 CE syndromes to UE. SoC checking reports IOB/XGIC/RB/PA/BA transaction errors and SoC parity sources.

## State and persistence behavior
All state is runtime-only. The driver persists child registration in linked lists, MCU active/registered bitmasks, EDAC control structures, debugfs dentries, and hardware MMIO/register bits. Interrupt mask updates are serialized with a spinlock; shared MCU top-level interrupt enable is serialized with `mc_lock` so the shared bit is not unmasked until all active MCUs are registered. No disk or cross-boot state is written.

## Dependencies and integration points
The file depends on device tree, platform devices, Linux EDAC core, EDAC debugfs, syscon regmaps, MMIO resources, IRQs, `ghes_get_devices()`, and X-Gene-specific DT child compatibles. It integrates with the EDAC core as both `mem_ctl_info` and `edac_device_ctl_info` providers, and exposes optional error-injection files when `CONFIG_EDAC_DEBUG` is enabled.

## Risks and edge cases
The shared MCU top-level interrupt can wedge if unmasked before all active MCUs register; the active/registered mask logic is the explicit mitigation. Many hardware status registers are write-to-clear or clear-by-writing-status, so incorrect ordering can lose diagnostics. Probe ignores child-add return values while continuing with other children, which makes partial EDAC coverage possible. L3 v1 syndrome promotion is hardware erratum-sensitive. Optional `rb_map` absence must not block SoC reporting. Debugfs injection writes synthetic error bits directly and is unsafe outside debug use.

## Test signals
Useful signals include boot probing with all DT child compatible variants, poll and interrupt modes, shared IRQ storms, inactive MCU and disabled-PMD filtering, GHES conflict behavior, MCU rank CE/UE injection, PMD L1/L2 debugfs injection, L3 erratum promotion cases, SoC IOB/RB/PA/BA transaction status clearing, remove/unload cleanup, and fault injection for missing phandles, missing IRQs, and failed resource maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/xgene_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/zynqmp_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/zynqmp_edac.c

## Purpose
`zynqmp_edac.c` implements EDAC-device support for Xilinx/AMD ZynqMP OCM ECC. It reports correctable and uncorrectable ECC events from OCM interrupt/status registers and optionally provides debugfs fault-injection controls.

## Important APIs, types, and functions
State lives in `struct edac_priv`, which stores the OCM MMIO base, EDAC message buffer, counters, current `struct ecc_status`, and debugfs injection fields. `get_error_info()` reads CE/UE fault address and data registers and clears the interrupt source. `handle_error()` formats EDAC messages and calls `edac_device_handle_ce()` or `edac_device_handle_ue()`. `intr_handler()` is the IRQ entry point. `edac_probe()` and `edac_remove()` own platform lifecycle. Debug builds add `inject_ce_write()`, `inject_ue_write()`, `write_fault_count()`, and `setup_debugfs()`.

## Control flow
Probe maps the OCM resource, refuses to bind if ECC is disabled in `ECC_CTRL_OFST`, allocates one EDAC device instance, requests the platform IRQ, enables CE/UE interrupts through `OCM_IEN_OFST`, creates debugfs entries when available, and registers the EDAC device. The IRQ handler reads `OCM_ISR_OFST`, ignores unrelated interrupts, collects either CE or UE details, increments total counters, reports through EDAC, and clears transient status. Removal disables CE/UE interrupts, removes debugfs, unregisters, and frees EDAC state.

## State and persistence behavior
The driver keeps runtime counters (`ce_cnt`, `ue_cnt`) and the last in-flight status in memory. Hardware keeps first-failing address/data registers until the handler clears CE/UE bits. Debugfs fault bit positions and fault count are stored in memory and written to OCM injection registers. There is no persistent storage.

## Dependencies and integration points
It depends on platform devices, OF match `xlnx,zynqmp-ocmc-1.0`, EDAC device APIs, MMIO, IRQs, and optional EDAC debugfs. It integrates with user diagnostics through EDAC logs/counters and debugfs injection files `inject_fault_count`, `inject_ue_bitpos`, and `inject_ce_bitpos`.

## Risks and edge cases
`get_error_info()` uses `if/else if`, so simultaneous CE and UE bits are handled one class per interrupt invocation. The UE debug path copies into `char buf[6]` and then writes `buf[len] = '\0'`; a full-size copy can index one byte past the array. Injection bit parsing must reject duplicate UE bit positions and bit positions above 63. Probe returns `-ENXIO` when firmware has not enabled ECC, so platform setup is a hard dependency.

## Test signals
Exercise probe with ECC enabled/disabled, CE and UE interrupts, interrupt clear behavior, debugfs CE/UE injection including invalid/duplicate bits and oversized counts, suspend/resume wake behavior through generic IRQ state, remove cleanup, and fault injection for IRQ request or EDAC registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/zynqmp_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/eisa/Kconfig

## Purpose
This Kconfig file defines the kernel configuration surface for legacy EISA bus support, including core EISA bus enumeration, VLB priming, PCI/EISA bridges, virtual root probing, and the optional EISA device-name database.

## Important APIs, types, and functions
The important symbols are `HAVE_EISA`, `EISA`, `EISA_VLB_PRIMING`, `EISA_PCI_EISA`, `EISA_VIRTUAL_ROOT`, and `EISA_NAMES`. There are no runtime functions in this file, but these symbols control which C files and generated headers are built.

## Control flow
`EISA` is a menuconfig gated by architecture-provided `HAVE_EISA`. `EISA_PCI_EISA` depends on PCI and excludes PARISC, while `EISA_VIRTUAL_ROOT` is limited to x86 EISA systems. `EISA_NAMES` enables a generated device-name table. Defaults favor legacy usability where EISA is already enabled.

## State and persistence behavior
The file has build-time state only. It changes compiled code and generated tables but has no runtime persistence.

## Dependencies and integration points
It integrates with Kbuild in the sibling Makefile and with architecture/platform code that selects `HAVE_EISA`. `EISA_NAMES` drives generation and inclusion of `devlist.h` from `eisa.ids`.

## Risks and edge cases
The virtual-root option is intentionally x86-only because forced probing on other architectures may crash. Enabling EISA_NAMES increases image size temporarily during boot. Disabling PCI bridge or virtual-root support can leave an EISA system without a root device to enumerate.

## Test signals
Relevant validation is Kconfig matrix coverage: `EISA=y/n`, x86/non-x86, PCI bridge enabled/disabled, virtual root enabled/disabled, and `EISA_NAMES` enabled/disabled with successful builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/eisa/Makefile

## Purpose
This Makefile wires EISA core, PCI bridge, virtual root, and generated name-table support into Kbuild.

## Important APIs, types, and functions
It builds `eisa-bus.o` for `CONFIG_EISA`, `pci_eisa.o` for `CONFIG_EISA_PCI_EISA`, and `virtual_root.o` for `CONFIG_EISA_VIRTUAL_ROOT`. It generates `devlist.h` from `eisa.ids` with a `sed` command that converts ID/name records to `EISA_DEVINFO()` initializers.

## Control flow
Kbuild first generates `devlist.h` when EISA is enabled, ensures `eisa-bus.o` depends on it, and cleans the generated file through `clean-files`. `virtual_root.o` is intentionally last so a real root bridge can register first.

## State and persistence behavior
There is no runtime state. The generated `devlist.h` is build output derived from `eisa.ids`.

## Dependencies and integration points
The file depends on Kbuild, the sibling `eisa.ids` database, and `include/linux/device.h` as a dependency trigger. It integrates directly with the Kconfig symbols defined in `Kconfig`.

## Risks and edge cases
The `sed` transform assumes a stable `eisa.ids` format. Object ordering matters for root registration: moving `virtual_root.o` earlier could let the virtual root consume the bus before a real bridge registers. Missing `devlist.h` generation breaks `CONFIG_EISA_NAMES` builds.

## Test signals
Build with `CONFIG_EISA=y` and `CONFIG_EISA_NAMES=y` to confirm `devlist.h` generation, with bridge and virtual-root toggles to confirm object inclusion and link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/eisa-bus.c -->
# sources/distributed-fs/ceph-client/drivers/eisa/eisa-bus.c

## Purpose
`eisa-bus.c` implements the Linux EISA bus type, sysfs exposure, root registration, slot probing, resource reservation, driver matching, module alias generation, and legacy `EISA_bus` export.

## Important APIs, types, and functions
The exported integration points are `eisa_bus_type`, `eisa_driver_register()`, `eisa_driver_unregister()`, and `eisa_root_register()`. Internally, `decode_eisa_sig()` reads slot signatures, `eisa_init_device()` fills `struct eisa_device`, `eisa_request_resources()` reserves per-slot IO windows, `eisa_register_device()` registers sysfs attributes, and `eisa_probe()` scans slot 0 plus configured card slots. Module parameters `enable_dev[]` and `disable_dev[]` force per-bus/slot state.

## Control flow
`postcore_initcall(eisa_init)` registers the bus. Root providers call `eisa_root_register()`, which reserves the root IO range under a global EISA root resource, assigns a bus number, and probes. Probing tries slot 0 mainboard first and may continue when `force_probe` is set. For each slot, it reserves resources, decodes the vendor signature, reads the enabled bit, applies forced enable/disable, names the device, registers it on the EISA bus, and creates `signature`, `enabled`, and `modalias` sysfs files.

## State and persistence behavior
Runtime state consists of registered device objects, reserved IO resources, the monotonic `eisa_bus_count`, forced-device module parameter arrays, and the exported `EISA_bus` integer for legacy drivers. Device state is in memory only and disappears on reboot.

## Dependencies and integration points
The file depends on IO port accessors (`inb`, optional `outb` VLB priming), resource management, Linux driver core, sysfs device attributes, `include/linux/eisa.h`, and optional generated `devlist.h`. Drivers match by EISA signature and receive modalias strings through uevents.

## Risks and edge cases
Slot probing uses direct IO and can be unsafe on non-EISA or incorrectly forced systems. Resource reservation failures skip devices and can abort mainboard probing unless forced. Forced enable/disable parameters override hardware state and may bind drivers to disabled hardware. Device-name lookup is freed after init, so names must be copied. Attribute creation failures must unwind registered devices and resources.

## Test signals
Boot on real or emulated EISA hardware, forced-probe paths, `enable_dev`/`disable_dev` parameters, sysfs attribute content, modalias-based module loading, resource conflict handling, driver match for enabled-only devices, and `CONFIG_EISA_NAMES` on/off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/eisa-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/pci_eisa.c -->
# sources/distributed-fs/ceph-client/drivers/eisa/pci_eisa.c

## Purpose
`pci_eisa.c` discovers generic PCI-to-EISA bridge devices and registers a real EISA root device backed by the bridge bus IO resource.

## Important APIs, types, and functions
The file centers on the static `pci_eisa_root` and two init helpers: `pci_eisa_init()` enables a found PCI bridge and populates the EISA root, while `pci_eisa_init_early()` walks PCI devices looking for `PCI_CLASS_BRIDGE_EISA`.

## Control flow
At `subsys_initcall_sync` time, after PCI subsystem setup but before PNP/ISA probing, the driver scans all PCI devices. For each EISA bridge, it enables the device, finds the first IO resource on the parent PCI bus, initializes `struct eisa_root_device` with that resource, maximum slots, base address, and DMA mask, stores it as driver data, and calls `eisa_root_register()`.

## State and persistence behavior
State is a single static root object plus driver data on the PCI device. It reserves IO resources indirectly through `eisa_root_register()`. There is no persistent state.

## Dependencies and integration points
It depends on PCI enumeration, PCI class codes, EISA root registration from `eisa-bus.c`, and early init ordering relative to x86 PCI and PNP/ISA code.

## Risks and edge cases
The code assumes one useful PCI/EISA bridge root and only passes one IO resource because the EISA core supports a single IO range. Missing bus IO resources or failed `pci_enable_device()` abort registration. Returning `-1` instead of a more specific errno limits diagnostics. Init ordering is critical to avoid PNP claiming resources first.

## Test signals
Validate on PCI/EISA bridge hardware or emulation, PCI resource absence, multiple bridges, early boot ordering with PNP enabled, and successful EISA slot enumeration through the registered root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/pci_eisa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/virtual_root.c -->
# sources/distributed-fs/ceph-client/drivers/eisa/virtual_root.c

## Purpose
`virtual_root.c` registers a fallback platform-device EISA root for systems without a discoverable PCI/EISA bridge, mainly x86 EISA-only systems.

## Important APIs, types, and functions
The file defines `eisa_root_dev`, `eisa_bus_root`, the `force_probe` module parameter, `virtual_eisa_release()`, and `virtual_eisa_root_init()`. It calls `platform_device_register()` and `eisa_root_register()`.

## Control flow
At `device_initcall`, the virtual platform device is registered, the root's `force_probe` flag is copied from the module parameter, driver data is set, and `eisa_root_register()` probes the default IO port resource from base 0 across `EISA_MAX_SLOTS`. If a real bridge already registered the same root resource, registration fails and the virtual platform device is quietly removed.

## State and persistence behavior
State is static runtime root/platform-device data and the `force_probe` parameter. There is no durable persistence.

## Dependencies and integration points
It depends on platform devices, the global `ioport_resource`, EISA core root registration, and Kconfig limiting this path to x86 EISA builds. `EISA_VLB_PRIMING` changes the default force-probe value.

## Risks and edge cases
Forced probing can touch IO ports on systems that do not actually have EISA. The driver intentionally loses to real root devices through resource conflict. Because the release callback is empty, all data must remain static.

## Test signals
Boot with and without a real PCI/EISA bridge, `force_probe=0/1`, resource conflict handling, VLB priming default behavior, and slot enumeration on EISA-only x86 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/eisa/virtual_root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/extcon/Kconfig

## Purpose
This Kconfig file defines the External Connector (extcon) subsystem option and all extcon provider driver symbols in this directory.

## Important APIs, types, and functions
The main symbol is `EXTCON`, with driver symbols such as `EXTCON_ADC_JACK`, `EXTCON_AXP288`, `EXTCON_FSA9480`, `EXTCON_GPIO`, Intel PMIC/ACPI variants, ON Semiconductor LC824206XA, Maxim MUIC drivers, USB GPIO, USB-C, Qualcomm, Richtek, Silicon Mitus, and Realtek Type-C entries. It selects dependencies such as `REGMAP_I2C`, `IRQ_DOMAIN`, and `USB_ROLE_SWITCH` where required.

## Control flow
`EXTCON` gates all provider drivers. Each child config encodes hardware bus dependencies and optional subsystem integrations. The resulting symbols drive the sibling Makefile object list.

## State and persistence behavior
This file has build-time state only. Runtime behavior is determined by which providers are compiled or built as modules.

## Dependencies and integration points
It integrates with I2C, GPIO, MFD PMICs, ACPI, power-supply, USB role-switch, Type-C, and architecture symbols. It is the policy layer that prevents impossible builds for hardware-specific extcon providers.

## Risks and edge cases
Incorrect dependencies can produce build failures or hidden runtime probe failures. Some entries allow `COMPILE_TEST`, so driver code must remain portable even without target hardware. USB role switch and Type-C dependencies are written to allow builds with or without those optional frameworks.

## Test signals
Run Kconfig/build matrices for each symbol as built-in and module where possible, with dependencies disabled/enabled, and compile-test cross-architecture coverage for drivers allowing it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/extcon/Makefile

## Purpose
The extcon Makefile maps extcon Kconfig symbols to core and provider objects.

## Important APIs, types, and functions
It builds `extcon-core.o` from `extcon.o` and `devres.o` when `CONFIG_EXTCON` is enabled, and adds one object per provider, including all files covered by this work item.

## Control flow
Kbuild includes the core for `CONFIG_EXTCON` and appends provider objects according to their `CONFIG_EXTCON_*` symbols. There is no runtime logic.

## State and persistence behavior
This is build-time-only state.

## Dependencies and integration points
It integrates the extcon core with platform, I2C, GPIO, PMIC, USB, and Type-C provider drivers selected in Kconfig.

## Risks and edge cases
Object names must stay aligned with source files and Kconfig symbols. Missing core object composition would break exported devres/provider APIs. Adding a new driver requires both Kconfig and Makefile entries.

## Test signals
Build each provider symbol as `y` and `m`, verify `extcon-core.o` includes both `extcon.o` and `devres.o`, and run allmodconfig/allnoconfig compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/devres.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/devres.c

## Purpose
`devres.c` provides device-managed wrappers for extcon device allocation/registration and notifier registration so providers and consumers can rely on automatic cleanup on driver detach.

## Important APIs, types, and functions
Exported APIs are `devm_extcon_dev_allocate()`, `devm_extcon_dev_free()`, `devm_extcon_dev_register()`, `devm_extcon_dev_unregister()`, `devm_extcon_register_notifier()`, `devm_extcon_unregister_notifier()`, `devm_extcon_register_notifier_all()`, and `devm_extcon_unregister_notifier_all()`. Internal release helpers call `extcon_dev_free()`, `extcon_dev_unregister()`, `extcon_unregister_notifier()`, and `extcon_unregister_notifier_all()`.

## Control flow
Allocation creates a devres slot, calls the unmanaged extcon API, assigns the parent device, stores the extcon pointer, and attaches the slot to the owner. Registration and notifier helpers allocate devres, perform the unmanaged registration, and add cleanup only after success. Manual devm unregister/free releases the matching devres entry.

## State and persistence behavior
State is held in devres records attached to the owning `struct device`. Cleanup is deterministic at manual release or automatic device detach. There is no persistence.

## Dependencies and integration points
It depends on the extcon core private header, Linux devres, and notifier APIs. It is used by many extcon provider drivers in this directory to simplify error paths.

## Risks and edge cases
`devm_extcon_unregister_notifier()` uses a match function that compares only `edev`, not `id` or `nb`, so multiple notifier devres entries on the same extcon device can release the wrong record. WARN paths catch missing records but do not recover. Callers must avoid mixing unmanaged unregister with devm-managed cleanup for the same object.

## Test signals
Probe-failure unwind tests, driver detach cleanup, manual devm unregister/free, multiple notifiers on one extcon device, notifier-all cleanup, and KASAN/lockdep coverage for use-after-free after provider removal are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-adc-jack.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-adc-jack.c

## Purpose
`extcon-adc-jack.c` reports external connector state by reading an IIO ADC channel and mapping configured ADC ranges to extcon cable IDs.

## Important APIs, types, and functions
`struct adc_jack_data` stores the extcon device, ADC conditions, IRQ, delay, IIO channel, work item, and wakeup flag. `adc_jack_handler()` reads ADC and sets matching cable state. `adc_jack_irq_thread()` schedules delayed work. `adc_jack_probe()` consumes platform data, allocates/registers extcon state, gets the IIO channel, requests IRQ, and runs initial detection. Suspend/resume manage delayed work and IRQ wake.

## Control flow
Probe requires platform data with `cable_names` and `adc_conditions`, counts conditions until `EXTCON_NONE`, gets the named IIO channel, registers the extcon device, requests an IRQ, enables wakeup if requested, and performs initial ADC detection. IRQs queue delayed work to let the signal settle. Work reads the ADC, marks the first matching condition true, or marks all configured conditions false if no range matches.

## State and persistence behavior
State is runtime-only in platform data references and `adc_jack_data`. Extcon state persists only in the extcon core until the next detection/removal.

## Dependencies and integration points
The driver depends on platform devices, IIO consumers, extcon provider APIs, IRQs, workqueues, and board/platform data from `linux/extcon/extcon-adc-jack.h`.

## Risks and edge cases
The code assumes `dev_get_platdata()` is non-NULL before dereferencing `pdata`. Only one matching ADC range is set true; it does not clear other cables when a new range matches, so overlapping or changing conditions can leave stale states. It uses unmanaged `request_any_context_irq()` and explicit `free_irq()`, so remove ordering matters. `cancel_work_sync(&data->handler.work)` targets delayed-work internals rather than `cancel_delayed_work_sync()`.

## Test signals
Test ADC ranges including no-match and overlapping ranges, IRQ debounce delay, initial state detection, missing platform data, IIO read errors, wakeup suspend/resume, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-adc-jack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-axp288.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-axp288.c

## Purpose
`extcon-axp288.c` handles USB charger-type detection and USB role switching for X-Powers AXP288 PMICs on Intel tablet platforms.

## Important APIs, types, and functions
`struct axp288_extcon_info` tracks PMIC regmap/IRQ data, extcon device, optional INT3496 ID extcon, USB role switch, role work, previous cable, and VBUS state. Core helpers are `axp288_handle_chrg_det_event()`, `axp288_get_vbus_attach()`, `axp288_usb_role_work()`, `axp288_get_id_pin()`, `axp288_extcon_enable()`, and `axp288_extcon_find_role_sw()`.

## Control flow
Probe gets parent AXP20x state, optionally locates the Cherry Trail xHCI role switch and INT3496 ID extcon, blocks P-unit I2C access while reading initial VBUS/reset-source information, registers extcon cables for SDP/CDP/DCP plus USB, maps PMIC IRQs through regmap-irq, registers an ID notifier if present, synchronizes role-switch state, starts BC1.2 detection, and enables wakeup. Interrupts synchronously run charger detection: read VBUS, ensure charger detection completed, decode SDP/CDP/DCP, clear old cable state, set new extcon states, and schedule USB role work if VBUS changed.

## State and persistence behavior
Runtime state includes `previous_cable`, `vbus_attach`, pending role work, and PMIC registers. Reset-source indicator bits are logged and cleared on probe. No durable state is stored.

## Dependencies and integration points
The driver depends on AXP20x MFD/regmap, regmap IRQs, IOSF MBI P-unit I2C locking, extcon, ACPI/software nodes, `usb_role_switch`, x86 CPU matching, and optional INT3496 extcon state.

## Risks and edge cases
PMIC register access must be wrapped with IOSF P-unit I2C blocking to avoid firmware collisions. Role-switch lookup can defer probe. Unknown BC1.2 results fall back to SDP. The driver uses the extcon state of another ACPI device if present, so probe ordering and notifier cleanup matter. Only VBUS rising IRQ is wake-enabled in suspend.

## Test signals
Validate SDP/CDP/DCP/no-VBUS detection, INT3496-present and absent role control, host/device/none role transitions, P-unit lock failure, regmap IRQ mapping failures, suspend wake on charger insertion, reset-source clearing, and probe deferral for the role switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-axp288.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-fsa9480.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-fsa9480.c

## Purpose
`extcon-fsa9480.c` supports Fairchild FSA9480-compatible microUSB switch/accessory detector chips over I2C, reporting USB, host, charger, line-out, video-out, and jig extcon states.

## Important APIs, types, and functions
`struct fsa9480_usbsw` stores device, regmap, extcon device, and cached device bitmask. `cable_types[]` maps hardware device-type bits to extcon cables. `fsa9480_detect_dev()` reads device-type registers and reports attach/detach deltas. `fsa9480_irq_handler()` clears interrupt registers and triggers detection. Probe initializes regmap, timing, automatic switching, interrupt masks, wakeup, and initial detection.

## Control flow
Probe requires an I2C IRQ, registers an extcon device, initializes an 8-bit regmap, sets ADC detect time to 500 ms, configures automatic switching, unmasks attach/detach interrupts, requests a falling-edge threaded IRQ, enables wakeup, and runs detection. On IRQ, it bulk-reads INT1/INT2 to clear latched interrupts and, if nonzero, reads DEV_T1/DEV_T2. It clears extcon states no longer present before setting newly attached states and updates the cached bitmask.

## State and persistence behavior
Runtime state is the cached 16-bit cable/device mask and hardware register configuration. No persistent state exists.

## Dependencies and integration points
The driver depends on I2C, regmap, extcon provider APIs, IRQs, wakeup support, and OF/I2C IDs for FSA9480/FSA880/TSU6111-compatible devices.

## Risks and edge cases
The device-type bit macros are ordinal bit numbers, and `cable_types[]` indexes them directly; incorrect definitions would misreport cables. The volatile register callback marks `INT1_MASK`, not the interrupt status registers, which is suspicious for caching behavior. Read failures in detection leave cached state unchanged. The driver reports multiple extcon cables per hardware type, so consumers must handle composite states.

## Test signals
Attach/detach each supported accessory type, multi-cable mappings, interrupt clear behavior, I2C/regmap read failures, wakeup suspend/resume, compatible variants, and initial detection on a cable already inserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-fsa9480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-gpio.c

## Purpose
`extcon-gpio.c` is a simple single-state extcon provider driven by one GPIO input and its IRQ.

## Important APIs, types, and functions
`struct gpio_extcon_data` stores the extcon device, delayed work, GPIO descriptor, extcon cable ID, debounce, and resume-check flag. `gpio_extcon_work()` reads the GPIO and synchronizes the extcon state. `gpio_irq_handler()` queues work. `gpio_extcon_probe()` acquires resources and runs initial detection.

## Control flow
Probe allocates private state, requests the `"extcon"` input GPIO, converts it to an IRQ, chooses rising or falling trigger based on active-low polarity, allocates/registers the extcon device, initializes devm-managed delayed work, requests the IRQ, stores driver data, and reads the initial state. Resume optionally queues another check when `check_on_resume` is set.

## State and persistence behavior
Runtime state is only the GPIO descriptor, extcon state, and delayed work. There is no persistence.

## Dependencies and integration points
The driver depends on GPIOLIB, extcon provider APIs, platform devices, IRQs, devm delayed-work helpers, and system power-efficient workqueues.

## Risks and edge cases
`extcon_id`, `debounce`, and `check_on_resume` are never populated from firmware or platform data in this file, so default zero values mean the provider reports cable ID 0 with no debounce unless another mechanism initializes the structure. The FIXME notes that extcon ID discovery is unresolved. IRQ triggering is single-edge based on active polarity, so detach transitions may be missed for level-stable GPIOs unless IRQ type is externally configured.

## Test signals
Probe with active-high and active-low GPIOs, initial state reporting, attach/detach IRQs, resume recheck, invalid GPIO-to-IRQ, missing firmware extcon ID support, and devm cleanup with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-cht-wc.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-cht-wc.c

## Purpose
`extcon-intel-cht-wc.c` manages USB ID/VBUS, charger detection, data-line muxing, optional VBUS boost, USB role switching, and optional power-supply reporting for Intel Cherry Trail Whiskey Cove PMIC power-source hardware.

## Important APIs, types, and functions
`struct cht_wc_extcon_data` tracks regmap, extcon device, optional role switch/regulator/power-supply, current USB type, previous cable, host state, and regulator state. Important helpers include `cht_wc_extcon_get_id()`, `cht_wc_extcon_get_charger()`, `cht_wc_extcon_pwrsrc_event()`, `cht_wc_extcon_set_phymux()`, `cht_wc_extcon_set_otgmode()`, `cht_wc_extcon_enable_charging()`, `cht_wc_extcon_sw_control()`, and board-specific role/regulator/power-supply setup.

## Control flow
Probe allocates/registers extcon state, applies model-specific quirks from the parent PMIC, optionally obtains the role switch and VBUS regulator, optionally registers a USB power-supply, enables PMIC software control, disables external charging initially, routes D+/D- to the PMIC when no host is detected, processes initial status, requests the power-source IRQ, and unmasks VBUS/USBID IRQs. IRQs read and later clear `CHT_WC_PWRSRC_IRQ`, then call `cht_wc_extcon_pwrsrc_event()`. That event reads ID/VBUS, enables OTG/boost and disables charging in host mode, otherwise enables charging and performs charger-type detection with an 800 ms timeout, updates extcon states, sets USB role, and notifies the power-supply if present.

## State and persistence behavior
The driver keeps `previous_cable`, `usb_host`, `usb_type`, and regulator state in memory while programming PMIC mux/control registers. No state is persisted beyond hardware register side effects during the driver lifetime.

## Dependencies and integration points
It depends on Intel SoC PMIC MFD data, regmap, extcon, power_supply, optional regulators, USB role-switch software nodes, and board model IDs. It reports both extcon cable states and, on selected boards, a USB power-supply used by charger drivers.

## Risks and edge cases
Board-specific quirks are central and regressions can cause battery drain, feedback loops, or wrong USB role. Charger detection falls back to SDP on timeout/failure. Host-mode 5V boost can create false VBUS detections, explicitly handled by skipping charger detection. Error paths after software control must disable it. Role-switch and regulator probe deferral affect selected models.

## Test signals
Test each PMIC model branch, host/device/none role transitions, no-VBUS detach, SDP/CDP/DCP/ACA charger detection and timeout fallback, power-supply property updates, external charger disable pin behavior, IRQ mask/clear behavior, and remove cleanup restoring hardware control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-cht-wc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-int3496.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-int3496.c

## Purpose
`extcon-intel-int3496.c` supports Intel INT3496 ACPI USB OTG control devices. It reads a USB ID GPIO, controls optional VBUS and USB mux GPIOs or a VBUS regulator, and reports `EXTCON_USB_HOST`.

## Important APIs, types, and functions
`struct int3496_data` stores GPIOs, optional regulator, extcon device, delayed work, IRQ, and VBUS regulator state. `int3496_do_usb_id()` is the role update worker. `int3496_thread_isr()` debounces ID changes. `int3496_set_vbus_boost()` wraps regulator enable/disable. ACPI GPIO mappings describe ID, VBUS, and mux GPIO indexes.

## Control flow
Probe installs ACPI GPIO mappings, allocates state and devm delayed work, gets the ID GPIO non-exclusively, maps it to an IRQ, optionally gets VBUS and mux GPIOs or a VBUS regulator, registers the extcon device, requests a shared threaded both-edge IRQ, queues and flushes initial ID processing, and stores driver data. The worker treats ID low as host, updates mux and VBUS controls accordingly, and synchronizes `EXTCON_USB_HOST`.

## State and persistence behavior
Runtime state is the last regulator enable state and GPIO outputs. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI, GPIO descriptors, regulators, extcon, platform devices, IRQs, and delayed work. AXP288 can use this device's extcon state as its ID source.

## Risks and edge cases
Some ACPI tables incorrectly mark the IRQ GPIO output-only, so the mapping uses `ACPI_GPIO_QUIRK_NO_IO_RESTRICTION`. If neither VBUS GPIO nor regulator is available, VBUS cannot be driven but host state is still reported. Work is debounced by a fixed 50 ms. Shared IRQs require robust filtering by GPIO state.

## Test signals
Exercise ACPI GPIO mapping, host/peripheral ID transitions, mux and VBUS GPIO output levels, optional regulator enable/disable, initial state after probe, probe without optional controls, and IRQ debounce.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-int3496.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-mrfld.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-mrfld.c

## Purpose
`extcon-intel-mrfld.c` reports USB host role and charger-related extcon capabilities for Intel Merrifield Basin Cove PMIC power-source hardware.

## Important APIs, types, and functions
`struct mrfld_extcon_data` stores device, regmap, extcon device, cached charger IRQ status, and PMIC ID. Important functions are `mrfld_extcon_get_id()`, `mrfld_extcon_role_detect()`, `mrfld_extcon_cable_detect()`, `mrfld_extcon_interrupt()`, and `mrfld_extcon_sw_control()`.

## Control flow
Probe gets the parent PMIC regmap and IRQ, registers extcon cables, requests a shared threaded IRQ, reads PMIC revision, enables software control, detects initial USB role, caches current charger IRQ status, unmasks charger/USB-ID interrupts, enables USB-ID detection, and stores driver data. IRQ handling compares current `BCOVE_SCHGRIRQ1` status against the cached status because firmware clears the normal IRQ register, runs role detection on USB-ID changes, updates the cache, and clears the PMIC top-level charger interrupt mask.

## State and persistence behavior
State is runtime-only: cached status, PMIC revision, extcon states, and PMIC control bits. Remove disables software control.

## Dependencies and integration points
The driver depends on Intel SoC PMIC MFD/regmap definitions, Basin Cove register definitions, extcon provider APIs, IRQs, and the shared Intel USB-ID enum from `extcon-intel.h`.

## Risks and edge cases
PMIC A0 and B0 invert/interpret the ground bit differently, so revision-specific logic is required. Firmware clearing IRQ registers forces cached-status comparison and can miss events if cache synchronization is wrong. The cable list includes charger types, but this implementation only updates host state. Interrupt return is `IRQ_NONE` on no detected status change.

## Test signals
Test PMIC A0/B0 ID decoding, ID ground/float/RID_A/B/C states, cached status changes, interrupt clearing, software-control enable/disable, and no-change IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-mrfld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel.h -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel.h

## Purpose
`extcon-intel.h` defines the shared Intel USB-ID classification enum used by Intel PMIC extcon drivers.

## Important APIs, types, and functions
The sole API is `enum extcon_intel_usb_id` with values for OTG, grounded ID, floating ID, and ACA RID_A/RID_B/RID_C states.

## Control flow
There is no executable control flow. Intel PMIC drivers return these enum values from hardware-specific ID decoders and map them to host/device/charger behavior.

## State and persistence behavior
No runtime state is defined.

## Dependencies and integration points
It is included by `extcon-intel-cht-wc.c` and `extcon-intel-mrfld.c` to keep ID classification consistent across hardware variants.

## Risks and edge cases
Enum semantics must remain aligned with users. Adding values requires auditing switch statements in Intel extcon drivers.

## Test signals
Compile coverage of Intel extcon drivers and switch-case coverage for each enum value in role-detection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-lc824206xa.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-lc824206xa.c

## Purpose
`extcon-lc824206xa.c` supports the ON Semiconductor LC824206XA microUSB switch/accessory detector. It reports USB host and charger types, controls a VBUS boost regulator, switches DP/DM routing, and exposes charger-detection data as a power-supply.

## Important APIs, types, and functions
`struct lc824206xa_data` stores work, I2C client, extcon, power-supply, VBUS regulator, cable/USB type, switch state, VBUS state, and a fast-charge quirk. Main helpers are `lc824206xa_work()`, `lc824206xa_charger_detect()`, `lc824206xa_get_id()`, `lc824206xa_set_vbus_boost()`, `lc824206xa_irq()`, and `lc824206xa_psy_get_prop()`.

## Control flow
Probe initializes undocumented chip registers, clears/masks interrupts, enables automatic ID ADC and charger detection, registers extcon and power-supply devices, requests a low-level threaded IRQ, and schedules initial work. IRQ handling reads/clears interrupt status and schedules work. Work reads status, computes valid VBUS vs OVP, optionally performs continuous ID ADC conversion, handles GND/ACA/float ID states, detects charger type for floating ID with VBUS, controls VBUS boost and switch routing, updates extcon cable state, and notifies the power-supply.

## State and persistence behavior
Runtime state includes current/previous cable, current/previous switch-control value, USB type, VBUS validity, and boost state. Register programming persists only while hardware remains powered.

## Dependencies and integration points
It depends on I2C SMBus byte access, extcon, regulator, power_supply, IRQs, workqueues, and an optional `onnn,enable-miclr-for-dcp` device property.

## Risks and edge cases
Register meanings are reverse-engineered from Android sources, so bit semantics may be incomplete. ID values during slow insertion can be transient and are partly handled with debug logs. Fast-charge-over-mic-L/R uses OVP as part of state recognition. IRQ clear requires writing bits then zero, so missed ordering can leave the line asserted. Work is not devm-autocancelled explicitly.

## Test signals
Test GND host, ACA, float no-VBUS, SDP/CDP/DCP/QC, OVP fast-charge quirk, VBUS boost regulator transitions, switch-control writes, power-supply current/USB type properties, IRQ clear behavior, and I2C error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-lc824206xa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14526.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14526.c

## Purpose
`extcon-max14526.c` supports the Maxim MAX14526 MUIC over I2C, reporting USB device, USB host, fast charger, and MHL extcon states while programming MUIC switch paths.

## Important APIs, types, and functions
`struct max14526_data` stores the I2C client, extcon device, regmap, regmap fields, last raw state, and current cable. `max14526_ap_usb_mode()` programs D+/D- to USB and enables charge pump/ADC. `max14526_interrupt()` delays for MUIC status stabilization, reads interrupt status, maps raw state to extcon cable, and updates state. Probe sets up regmap fields, verifies vendor ID, registers extcon, configures USB mode, enables interrupts, and triggers initial detection with `irq_wake_thread()`.

## Control flow
On IRQ, the handler sleeps 100 ms, reads `MAX14526_INT_STAT`, ignores duplicate state, clears the previous extcon cable, switches on composite status values such as USB, charger, OTG, MHL, or none, then sets the new extcon cable and records `last_state`. Resume wakes the IRQ thread to refresh state.

## State and persistence behavior
The driver keeps `last_state` and current cable in memory, and writes MUIC control registers for switch path and detection. There is no persistent storage.

## Dependencies and integration points
It depends on I2C, regmap/regmap fields, extcon provider APIs, threaded IRQs, and OF/I2C IDs for `maxim,max14526`.

## Risks and edge cases
The vendor-ID mismatch path calls `dev_err_probe()` but does not return, so unsupported IDs continue probing. `dev_err_probe(dev, (IS_ERR(priv->edev)), ...)` passes a boolean instead of the real error code on extcon allocation failure. Raw state matching relies on enum values ORed with status bits; unexpected bit combinations map to `EXTCON_NONE`.

## Test signals
Verify ID/revision detection, USB/charger/OTG/MHL/no-cable state mapping, duplicate IRQ suppression, initial IRQ thread wake, resume refresh, regmap read/write failures, and unsupported vendor ID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14526.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14577.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14577.c

## Purpose
`extcon-max14577.c` supports the MUIC block in Maxim MAX14577 and MAX77836 devices, reporting USB, charger, and jig extcon states and switching internal USB/UART paths.

## Important APIs, types, and functions
`struct max14577_muic_info` stores parent MFD state, extcon, previous ADC/charger classifications, status bytes, IRQ metadata, coalescing flags, work items, mutex, and default USB/UART paths. Core helpers are `max14577_muic_get_cable_type()`, `max14577_muic_set_path()`, `max14577_muic_adc_handler()`, `max14577_muic_chg_handler()`, `max14577_muic_irq_handler()`, `max14577_muic_irq_work()`, and `max14577_muic_detect_accessory()`.

## Control flow
Probe chooses the IRQ list for MAX14577 or MAX77836, maps nested regmap IRQs to virqs, requests each threaded IRQ, registers the extcon device, sets default USB/UART paths, reads initial status to route UART jig early, reads revision, sets ADC debounce, and queues delayed cable detection after boot. Nested IRQ handlers only classify whether ADC and/or charger work is needed, then schedule work. Work reads two MUIC status registers under a mutex and invokes ADC and charger handlers. ADC handling supports jig USB/UART cables and logs unsupported accessories. Charger handling reports USB SDP, DCP, CDP, special slow/fast chargers, and path switching for USB.

## State and persistence behavior
State is runtime-only: cached previous ADC and charger type allows detach reporting when hardware returns open/none, while status bytes are refreshed per event. Hardware control registers hold path and debounce configuration.

## Dependencies and integration points
It depends on the MAX14577 MFD/regmap/irq-domain support, extcon provider APIs, workqueues, mutexes, and platform/OF IDs for both MAX14577 and MAX77836 MUIC variants.

## Risks and edge cases
Delayed detection uses a long default 17 second delay to wait for platform boot. Unsupported ADC accessories return `-EAGAIN` and only log. IRQ coalescing uses boolean flags, so repeated events before work runs collapse into one status read. Correct detach reporting depends on previous type caches. MAX77836 has extra IRQs and must use the right parser.

## Test signals
Test MAX14577 and MAX77836 IRQ mapping, USB/JIG/DCP/CDP/slow/fast charger attach/detach, UART jig early path setup, delayed boot detection, simultaneous ADC and charger IRQs, unsupported ADC accessories, and regmap failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14577.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max3355.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max3355.c

## Purpose
`extcon-max3355.c` supports Maxim MAX3355 USB OTG role detection using GPIOs. It reports USB host vs simulated USB peripheral state through extcon.

## Important APIs, types, and functions
`struct max3355_data` stores the extcon device, ID GPIO, and shutdown GPIO. `max3355_id_irq()` reads the ID pin and updates `EXTCON_USB_HOST` and `EXTCON_USB`. Probe gets GPIOs, registers extcon, requests a both-edge threaded IRQ, and performs initial detection. Remove drives shutdown low.

## Control flow
Probe requests `"id"` as input and `"maxim,shdn"` as output high, registers extcon cables for USB and USB_HOST, maps the ID GPIO to IRQ, requests a no-suspend both-edge IRQ, stores driver data, and calls the IRQ handler once. The handler treats ID high as host detached and simulates USB peripheral attached; ID low clears USB peripheral and reports USB host.

## State and persistence behavior
Runtime state is entirely GPIO and extcon state. Shutdown GPIO level changes at probe/remove; no persistent state exists.

## Dependencies and integration points
It depends on GPIO descriptors, platform devices, OF match `maxim,max3355`, IRQs, and extcon provider APIs.

## Risks and edge cases
Because the chip only exposes ID role, the driver simulates peripheral attach when host is absent; this may be wrong if nothing is connected. IRQ is marked `IRQF_NO_SUSPEND`, so it can run during suspend. Shutdown GPIO polarity/configuration must match board wiring.

## Test signals
Test ID high/low transitions, initial state, shutdown GPIO on remove, GPIO-to-IRQ failure, suspend behavior, and consumer reaction to simulated USB peripheral state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max3355.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77693.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77693.c

## Purpose
`extcon-max77693.c` supports the Maxim MAX77693 MUIC, reporting USB, host, charger, MHL, jig, and dock extcon states while handling dock button input events and programming MUIC switch paths.

## Important APIs, types, and functions
`struct max77693_muic_info` stores parent MFD state, extcon, previous ADC/GND/charger/button classifications, status bytes, current IRQ, work items, mutex, dock input device, and USB/UART paths. Major helpers are `max77693_muic_get_cable_type()`, `max77693_muic_set_path()`, `max77693_muic_adc_ground_handler()`, `max77693_muic_jig_handler()`, `max77693_muic_dock_handler()`, `max77693_muic_dock_button_handler()`, `max77693_muic_adc_handler()`, `max77693_muic_chg_handler()`, `max77693_muic_irq_work()`, and `max77693_muic_detect_accessory()`.

## Control flow
Probe initializes or reuses the MUIC regmap, registers a dock input device, maps and requests all nested MUIC IRQs, registers extcon, applies platform or default MUIC initialization registers, sets USB/UART paths and delayed detection time, routes UART jig early if present, reads device ID, configures ADC debounce, and queues delayed initial detection. IRQ handler records the virq and schedules work. Work maps the virq back to a MUIC interrupt type, reads STATUS1/STATUS2 under a mutex, dispatches ADC-family events to accessory/dock/jig/button handling, and dispatches charger-family events to charger and composite MHL/dock charging handling.

## State and persistence behavior
The driver keeps previous ADC, ADC-ground, charger, and button classifications so detach and button release can be reported after hardware returns open states. Hardware registers store path, low-power/charge-pump, debounce, and interrupt-mask configuration. There is no persistent storage.

## Dependencies and integration points
It depends on MAX77693 MFD/regmap/irq-domain support, extcon provider APIs, Linux input for dock keys, workqueues, mutexes, platform data or OF match, and EDAC-independent MFD initialization.

## Risks and edge cases
The global `muic_irqs[]` stores virqs and is shared across device instances, so multiple devices would overwrite IRQ mappings. Work records only one `info->irq`, so rapid different IRQs before work runs can collapse or be misclassified. Composite MHL/dock plus charger cases have ordering assumptions between ADC and charger IRQs. The default initial detection delay is 20 seconds, so early consumers may see stale state.

## Test signals
Test USB host, USB SDP, DCP, CDP, Apple slow/fast chargers, MHL with/without VBUS, smart/audio docks, jig USB/UART, dock buttons, simultaneous ADC/charger IRQ ordering, delayed initial detection, multiple-instance behavior, and regmap/input allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77693.c -->
