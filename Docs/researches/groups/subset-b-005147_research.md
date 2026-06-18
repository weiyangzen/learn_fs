# Research: subset-b-005147

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/touchscreen_dmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/touchscreen_dmi.c

Purpose: DMI keyed touchscreen quirk data for x86 tablets and convertibles whose ACPI tables do not describe touchscreen geometry, orientation, firmware, or controller quirks well enough for generic drivers. The file is mostly a sorted database of `struct property_entry` arrays and `struct ts_dmi_data` records; each record names an ACPI/I2C device prefix such as `MSSL1680:00` or `GDIX1001`, optional `efi_embedded_fw_desc`, and a property list for the actual touchscreen driver.

Important APIs and control flow: `touchscreen_dmi_table` is exported for EFI embedded firmware matching. `ts_dmi_init()` runs as an `arch_initcall`, finds the first DMI match, honors the `i2c_touchscreen_props=` command-line override, and registers an I2C bus notifier before ACPI enumeration. On `BUS_NOTIFY_ADD_DEVICE`, `ts_dmi_notifier_call()` verifies the device as an I2C client and `ts_dmi_add_props()` attaches a managed software node when the client has an ACPI companion and its name starts with the selected `acpi_name`. `ts_parse_props()` accepts colon-separated bool, u32, and string properties.

State and persistence: global `ts_data` selects one active quirk table for the boot. Command-line property strings are retained from the static command line, and EFI firmware descriptors are copied from matching DMI data when a command-line override supplies properties. Properties are device-managed after attachment and are not persistent beyond the device lifetime.

Dependencies and integration: depends on DMI, ACPI companion checks, I2C bus notifications, firmware property/software node APIs, and EFI embedded firmware matching. Downstream consumers are Silead, Goodix, Chipone, and other touchscreen drivers that read standard `touchscreen-*`, `firmware-name`, and vendor properties.

Risks and test signals: overly broad DMI matches can attach wrong calibration or firmware; many entries therefore include BIOS date/version/SKU matches. The notifier must run early enough that touchscreen clients see properties at probe. Useful tests include booting matched tablets, confirming `/sys/firmware/dmi` match selection, verifying software node properties on the I2C client, checking embedded firmware hash extraction, and exercising the command-line parser with bool/u32/string values and syntax failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/touchscreen_dmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Kconfig

Purpose: top-level Kconfig include point for TUXEDO x86 platform drivers. It currently delegates all selectable options to `drivers/platform/x86/tuxedo/nb04/Kconfig`.

Important APIs and control flow: this file has no runtime APIs. Its only active statement is `source "drivers/platform/x86/tuxedo/nb04/Kconfig"`, so menu visibility, dependencies, and module descriptions are defined in the nested Kconfig.

State and dependencies: there is no state or persistence. The integration point is the kernel Kconfig parser and the parent `drivers/platform/x86` menu.

Risks and test signals: a bad source path hides all TUXEDO NB04 options from configuration. Tests are configuration-oriented: run `make olddefconfig`, `make menuconfig`, or Kconfig lint and confirm `CONFIG_TUXEDO_NB04_WMI_AB` is reachable through the platform x86 drivers menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Makefile

Purpose: build routing for the TUXEDO platform-driver subtree. It unconditionally descends into the `nb04/` subdirectory via `obj-y += nb04/`.

Important APIs and control flow: no C symbols are defined here. Kbuild visits `nb04/Makefile`, where object inclusion is gated by `CONFIG_TUXEDO_NB04_WMI_AB`.

State and dependencies: no runtime state. It depends on Kbuild directory traversal and the parent platform/x86 Makefile including this directory.

Risks and test signals: if this Makefile is not reached, NB04 driver objects never build even when Kconfig is enabled. Build tests should confirm `drivers/platform/x86/tuxedo/nb04/tuxedo_nb04_wmi_ab.o` appears for `CONFIG_TUXEDO_NB04_WMI_AB=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Kconfig

Purpose: defines the selectable NB04 WMI AB platform driver option. `TUXEDO_NB04_WMI_AB` is a tristate driver for TUXEDO notebooks with NB04 board vendor firmware, exposing keyboard backlight control through a virtual HID LampArray device.

Important APIs and control flow: no runtime code. The option depends on `ACPI_WMI` and `HID`, and its help text documents the module name `tuxedo_nb04_wmi_ab`.

State and dependencies: the Kconfig state controls whether the WMI/HID source files are built-in, modular, or omitted. Runtime dependencies are declared here so the driver has WMI registration and HID virtual device APIs available.

Risks and test signals: missing `HID` or `ACPI_WMI` dependencies would cause build failures. Configuration tests should cover `n`, `m`, and `y`, and module builds should verify the resulting module name matches the help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Makefile

Purpose: Kbuild recipe for the TUXEDO NB04 WMI AB module. It composes `tuxedo_nb04_wmi_ab.o` from `wmi_ab.o` and `wmi_util.o`.

Important APIs and control flow: no runtime APIs. `obj-$(CONFIG_TUXEDO_NB04_WMI_AB)` gates the composite object, while `tuxedo_nb04_wmi_ab-y` lists the constituent objects.

State and dependencies: build state is entirely driven by `CONFIG_TUXEDO_NB04_WMI_AB`. The composition ties the virtual HID LampArray implementation to the WMI method helper layer.

Risks and test signals: omitting `wmi_util.o` would leave unresolved WMI wrapper symbols, while a wrong composite name would break the documented module name. Test by building the option as a module and checking symbol resolution with `modpost`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_ab.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_ab.c

Purpose: WMI-backed virtual HID LampArray driver for tested TUXEDO NB04 notebooks. It registers on WMI GUID `80C9BAA6-AC48-4538-9234-9F81A55E7C85`, creates a virtual HID device named `TUXEDO NB04 RGB Lighting`, and translates HID Lighting and Illumination feature reports into NB04 WMI keyboard-backlight commands.

Important APIs and types: `tux_report_descriptor` describes LampArray feature reports. `struct tux_kbl_map_entry_t` maps HID lamp IDs to keyboard usage codes and physical positions for Sirius 16 ANSI/ISO layouts. `struct tux_hdev_driver_data_t` stores lamp count, selected key map, next attribute response lamp, and a pending `TUX_KBL_SET_MULTIPLE_KEYS` WMI input buffer. The HID low-level driver implements `.start`, `.parse`, and `.raw_request`; WMI probe/remove allocate and destroy the virtual HID device.

Control flow: module init first DMI-gates to Sirius 16 Gen1/Gen2 board names, then registers the WMI driver. HID start calls `tux_wmi_xx_8in_80out(TUX_GET_DEVICE_STATUS)` to choose ANSI or ISO layout. GET_REPORT returns array attributes and per-lamp attributes. SET_REPORT handles attribute requests, multi updates, range updates, and a no-op array-control report. Multi/range updates accumulate key RGB values in the 496-byte WMI input and flush only when `LAMP_UPDATE_COMPLETE` is set.

State and dependencies: state is per HID device and device-managed, with WMI output not persisted by the driver. Integration spans WMI, HID core, DMI matching, and the helper ABI in `wmi_util.h`.

Risks and test signals: lamp ID bounds, duplicate detection, and deferred flush behavior are critical. The multi-update check uses `rep->lamp_id[i] > driver_data->lamp_count`, so `lamp_id == lamp_count` should be tested because valid indices end at `lamp_count - 1`. Tests should cover ANSI/ISO detection, HID descriptor parsing, GET/SET feature report sizes, range splitting into batches of eight, intensity scaling, WMI failure propagation, remove-time HID destruction, and DMI refusal on untested machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_ab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.c

Purpose: shared WMI method helper layer for TUXEDO NB04 drivers. It hides ACPI buffer setup, WMI method evaluation, output type validation, and fixed-size buffer copying.

Important APIs and control flow: `__wmi_method_acpi_object_out()` builds input/output `acpi_buffer` structures, calls `wmidev_evaluate_method()`, and returns an allocated ACPI object. `__wmi_method_buffer_out()` wraps it, requires `ACPI_TYPE_BUFFER`, checks the returned length is at least the expected size, and copies bytes to the caller's union. Public wrappers `tux_wmi_xx_8in_80out()` and `tux_wmi_xx_496in_80out()` bind method IDs to the NB04 ABI sizes.

State and dependencies: no persistent state. It depends on the WMI core, ACPI object lifetimes, `__free(kfree)` cleanup, and the packed ABI unions declared in `wmi_util.h`.

Risks and test signals: wrong buffer sizes corrupt firmware calls or truncate outputs; non-buffer ACPI returns and short buffers must fail. Debug hex dumps may expose raw firmware inputs when dynamic debug is enabled. Tests should mock or exercise WMI methods for success, ACPI failure, null output, wrong object type, short output, and exact/oversized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.h

Purpose: ABI declaration for TUXEDO NB04 WMI method wrappers. It defines device-status constants, keyboard layout and lighting enums, fixed-size input/output unions, and public helper prototypes.

Important APIs and types: `union tux_wmi_xx_8in_80out_in_t/out_t` models the 8-byte input and 80-byte output for `TUX_GET_DEVICE_STATUS`. `union tux_wmi_xx_496in_80out_in_t/out_t` models the 496-byte input and 80-byte output for `TUX_KBL_SET_MULTIPLE_KEYS`, including up to 120 RGB key configurations. Enums define WMI method IDs `2` and `6`.

State and dependencies: no state. The header depends on `<linux/wmi.h>` and packed layout matching the firmware ABI exactly. It is consumed by both the WMI helper implementation and the virtual LampArray driver.

Risks and test signals: all structure offsets are firmware contract. Any packing, count, or method-ID change must be validated against real NB04 firmware. Build tests should include sparse/compile coverage, and runtime tests should confirm `sizeof()` for the unions remains 8, 80, 496, and 80 bytes respectively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Kconfig

Purpose: Kconfig menu for Uniwill-derived laptop platform support. `X86_PLATFORM_DRIVERS_UNIWILL` opens the submenu and `UNIWILL_LAPTOP` builds the extras driver.

Important APIs and control flow: `UNIWILL_LAPTOP` is tristate, defaults to module, depends on ACPI, WMI, ACPI battery, hwmon, input, multicolor LED, and DMI support, and selects `REGMAP` plus `INPUT_SPARSEKMAP`.

State and dependencies: configuration state decides whether the composite `uniwill-laptop` driver builds. The dependency list mirrors runtime subsystems used by `uniwill-acpi.c` and `uniwill-wmi.c`.

Risks and test signals: missing dependencies surface as compile or link failures in hwmon, LED, input, battery hook, or WMI paths. Test by compiling `UNIWILL_LAPTOP=m` and `=y` in representative x86 configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Makefile

Purpose: Kbuild recipe for the Uniwill laptop platform driver. It creates the composite object `uniwill-laptop.o` from `uniwill-acpi.o` and `uniwill-wmi.o`.

Important APIs and control flow: `obj-$(CONFIG_UNIWILL_LAPTOP)` gates the composite object. The object list ensures the ACPI EC platform driver and the WMI event bridge are linked into one module or built-in unit.

State and dependencies: no runtime state. It depends on Kbuild composite-object semantics and the matching Kconfig symbol.

Risks and test signals: object order matters because the ACPI file calls `uniwill_wmi_register_driver()` from module init. Build tests should verify no unresolved notifier/WMI symbols and that the module name is `uniwill-laptop`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-acpi.c

Purpose: main Uniwill notebook extras driver. It exposes EC-backed sysfs controls, hwmon sensors, multicolor lightbar LED control, battery health/charge-threshold extensions, hotkey input, and suspend/resume restoration for selected Uniwill/TUXEDO/Schenker/Intel systems.

Important APIs and types: `struct uniwill_data` owns the ACPI handle, EC regmap, feature bitmap, battery hook/list, locks, LED class device, input device, WMI notifier, and cached restore state. `struct uniwill_device_descriptor` supplies DMI-selected feature flags and optional probe callbacks. The regmap bus maps `ECRR`/`ECRW` ACPI methods to 16-bit EC registers with 8-bit values. Sysfs attributes include `fn_lock`, `super_key_enable`, `touchpad_toggle_enable`, `rainbow_animation`, `breathing_in_suspend`, `ctgp_offset`, and `usb_c_power_priority`.

Control flow: module init DMI-matches a descriptor unless `force` is set, registers the platform driver, then manually registers the Uniwill WMI event driver. Platform probe initializes regmap, enables EC manual control, applies descriptor/probe-derived features, then initializes battery hooks, lightbar, hwmon, NVIDIA CTGP, USB-C priority, and input/WMI notifications. Notifier events refresh batteries, restore USB-C power priority on AC changes, notify fn-lock sysfs, or report sparse-keymap input events.

State and persistence: EC state is modified in hardware and partially cached in regmap. Driver state caches charge control, fn-lock, super-key, and USB-C priority for suspend/resume. Manual EC control is cleared by devm action and shutdown. Battery list membership is protected by `battery_lock`; super key, LED writes, input reports, and USB-C priority have dedicated locks.

Dependencies and integration: depends on ACPI methods `ECRR`/`ECRW`, DMI descriptors, regmap, hwmon, LED multicolor, power-supply extension APIs, ACPI battery hooks, input sparse-keymap, and `uniwill-wmi.c` notifier delivery.

Risks and test signals: EC register semantics are model-specific, so DMI feature descriptors are safety-critical. Suspend/resume restore paths must not desynchronize volatile registers. Tests should verify each visible sysfs attribute only appears for supported features, EC manual control is cleared on removal/shutdown, hwmon values scale correctly, LED AC/battery registers stay in sync, battery extensions unregister cleanly, WMI events produce expected input/sysfs/power-supply updates, and DMI-gated probe rejects unsupported systems unless forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.c

Purpose: WMI event bridge for the Uniwill laptop driver. It listens for a known Uniwill-style event GUID and forwards integer event payloads to registered notifier blocks.

Important APIs and control flow: `devm_uniwill_wmi_register_notifier()` registers a notifier in `uniwill_wmi_chain_head` and arranges devm unregister. `uniwill_wmi_notify()` accepts only integer ACPI objects, logs the event value, and calls the blocking notifier chain. `uniwill_wmi_register_driver()` and `uniwill_wmi_unregister_driver()` are called manually by `uniwill-acpi.c`.

State and dependencies: global blocking notifier chain is the only persistent state. The WMI driver uses GUID `ABBC0F72-8EA1-11D1-00A0-C90629100000`, `min_event_size = sizeof(u32)`, and `no_singleton = true`.

Risks and test signals: the GUID is intentionally not trusted for autoloading because it may be copied by unrelated firmware; manual DMI-gated registration limits false binding. Tests should cover integer and non-integer WMI events, notifier registration/unregistration lifetime, multiple WMI devices, and behavior when the WMI driver cannot register after the ACPI platform driver is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.h

Purpose: shared event-code and notifier API header for Uniwill WMI hotkey events. It names OSD/event constants used by the WMI bridge and ACPI driver.

Important APIs and types: defines event IDs for lock keys, touchpad, radio, webcam, brightness, lightbar, fan, battery, USB/DC adapter, performance mode, keyboard illumination, mic mute, fn lock, and other OEM notifications. Declares `devm_uniwill_wmi_register_notifier()`, `uniwill_wmi_register_driver()`, and `uniwill_wmi_unregister_driver()`.

State and dependencies: no state. The header depends on init annotations and forward declarations for `struct device` and `struct notifier_block`.

Risks and test signals: event-code meanings are firmware ABI and some are ignored or uncertain in the consumer. Tests should verify keymap mappings in `uniwill-acpi.c` stay aligned with these constants and that new constants do not collide.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uv_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/uv_sysfs.c

Purpose: builds `/sys/firmware/sgi_uv` topology for HPE SGI UV systems. It exposes partition/coherency/type attributes, hub objects, hub ports, and PCI bus topology derived from UV BIOS calls; hubless systems receive a smaller base group.

Important APIs and control flow: init first rejects non-UV systems, creates `sgi_uv`, and branches to hubless or full setup. Full setup creates base attributes, installs the UV BIOS heap, enumerates hub objects (`uv_bios_enum_objs`), ports (`uv_bios_enum_ports`), and PCI topology text (`uv_bios_get_pci_topology`). Custom kobject types expose hub attributes (`name`, `location`, `this_partition`, `shared`, `nasid`, `cnode`), port connection attributes, and parsed PCI topology attributes (`type`, `location`, `iio_stack`, `ppb_addr`, `slot`).

State and persistence: globals hold ksets, BIOS buffers, kobject arrays, object-to-cnode cache, BIOS heap, counts, and master NASID for the module lifetime. Data is generated at init and released in reverse order on exit.

Dependencies and integration: depends on UV architecture helpers and BIOS interfaces from `asm/uv/*`, kobject/sysfs APIs, and firmware kobject hierarchy. PCI topology parsing mutates BIOS text lines to construct kobject names.

Risks and test signals: unwind paths are complex and must avoid leaks or double puts. Firmware text parsing is format-sensitive, and object ID/count assumptions must stay within allocated arrays. Tests should boot full UV and hubless UV configurations, inspect sysfs tree shape and attribute values, inject BIOS errors for each setup stage if possible, and run module unload/reload with leak and kobject warnings enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/uv_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/winmate-fm07-keys.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/winmate-fm07-keys.c

Purpose: polled input driver for five front-panel keys on Winmate FM07/FM07P systems. It reads an embedded-controller key byte through fixed I/O ports and reports keys as `KEY_F13` through `KEY_F17`.

Important APIs and control flow: module init DMI-gates on Winmate `IP30`, registers a platform driver, and creates a simple platform device. Probe allocates an input device, reserves command/data ports `0x6c` and `0x68`, enables EV_KEY bits, sets up polling with `fm07keys_poll()`, and registers the device. Polling flushes EC output, writes the read command and key address, waits for data ready, reads active-low bits, reports each key, and syncs.

State and dependencies: state is the platform device pointer and the input device managed by devres. It depends on DMI, legacy I/O port access, input polling, and platform device registration.

Risks and test signals: polling busy-waits up to `LOOP_TIMEOUT` without sleeps, so port behavior and timeout logging matter. Fixed ports can conflict with other EC users. Tests should confirm DMI gating, port reservation failure handling, 50 Hz polling behavior, active-low key mapping, timeout ratelimiting, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/winmate-fm07-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/wireless-hotkey.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/wireless-hotkey.c

Purpose: ACPI platform driver that turns firmware airplane-mode button notifications into `KEY_RFKILL` input events for AMD, HP, Xiaomi, and LG-style ACPI IDs.

Important APIs and control flow: ACPI IDs include `HPQ6001`, `WSTADEF`, `AMDI0051`, and `LGEX0815`. Probe allocates `struct wl_button`, creates and registers an input device named `Wireless hotkeys`, and installs an ACPI device notify handler. `wl_notify()` only treats event `0x80` as a key press/release pulse; other events are logged. Remove unregisters the notify handler and input device.

State and dependencies: per-device state stores the input device and physical path string. The driver depends on ACPI companion devices, platform-driver ACPI matching, and input core.

Risks and test signals: input allocation is manual rather than devm, making remove/error path correctness important. Unknown event logging can become noisy if firmware emits additional notifications. Tests should cover ACPI matching, event `0x80` press/release ordering, unknown events, probe failure after input registration, and remove-time notify teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/wireless-hotkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/wmi-bmof.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/wmi-bmof.c

Purpose: exposes WMI embedded Binary MOF data through a binary sysfs attribute for devices advertising GUID `05901221-D566-11D1-B2F0-00A0C9062910`.

Important APIs and control flow: probe allocates `struct wmi_buffer`, calls `wmidev_query_block()` for instance 0, and stores the buffer as driver data. The `bmof` binary attribute is admin-readable, reports size from `buffer->length`, and serves reads through `memory_read_from_buffer()`. Remove frees `buffer->data` allocated by the WMI query.

State and dependencies: per-WMI-device state is the queried binary buffer. Integration is with WMI block query APIs and sysfs binary attributes attached through driver `dev_groups`.

Risks and test signals: ownership of `buffer->data` is split from devm allocation and must be freed exactly once. Tests should verify sysfs size/read behavior, partial reads and offsets, no data exposure to unprivileged users, multiple WMI devices with `no_singleton`, query failure handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/wmi-bmof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Kconfig

Purpose: configuration for the x86 Android tablet DSDT-fixup driver. It targets tablets whose factory Android kernels hardcoded devices, GPIOs, and addresses that firmware failed to describe reliably.

Important APIs and control flow: `X86_ANDROID_TABLETS` is tristate and depends on I2C, SPI, serial device bus, GPIO, PMIC opregion, ACPI, EFI, and PCI. It selects LED and power-supply support used by instantiated board devices.

State and dependencies: the Kconfig symbol controls both the main fixup driver and the Vexia EC battery driver in the Makefile.

Risks and test signals: this driver is broad and DMI-gated at runtime, so generic distro configs are expected to build it as a module. Configuration tests should verify all selected subsystems are available and the module builds in x86 allmodconfig-like environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Makefile

Purpose: Kbuild composition for x86 Android tablet support. It builds `vexia_atla10_ec.o` and a composite `x86-android-tablets.o` when `CONFIG_X86_ANDROID_TABLETS` is enabled.

Important APIs and control flow: the composite object includes `core.o`, `dmi.o`, `shared-psy-info.o`, and board files `acer.o`, `asus.o`, `lenovo.o`, and `other.o`.

State and dependencies: no runtime state. Object composition binds the central DMI/core machinery with per-vendor `x86_dev_info` records and shared power-supply software-node data.

Risks and test signals: missing a board object would leave extern declarations unresolved or DMI entries without data. Build tests should verify both built-in and module configurations and confirm `MODULE_DEVICE_TABLE(dmi, x86_android_tablet_ids)` is present in the composite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/acer.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/acer.c

Purpose: Acer board manifests for the x86 Android tablet fixup driver. It describes missing devices and software properties for Acer Iconia One 8 A1-840 and Acer Iconia One 7 B1-750.

Important APIs and data: exports `acer_a1_840_info` and `acer_b1_750_info` as `struct x86_dev_info`. A1-840 instantiates a BQ24297 charger, MPU6515 sensor, FT5416 touchscreen, an `intel-int3496` USB ID platform device, generic LiPo battery software nodes, and a custom init hook that attaches fuel-gauge properties to the existing `chtdc_ti_battery` device. B1-750 instantiates Novatek touchscreen and BMA250E accelerometer with mount matrix and reset/IRQ GPIO properties.

State and dependencies: board data is mostly `__initconst`; A1-840 has global pointers for the fuel-gauge device and software node until exit. Integration depends on Bay Trail GPIO software nodes, shared power-supply metadata, I2C client instantiation, GPIO IRQ helpers, and platform device registration in `core.c`.

Risks and test signals: A1-840 intentionally leaks the software node on exit to avoid dangling `supplied-from` string references in another driver. Tests should verify deferred probing until `chtdc_ti_battery` exists, charger module preloading, GPIO polarity, I2C addresses/adapters, touchscreen reset, and cleanup of device references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/acer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/asus.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/asus.c

Purpose: Asus board manifests for x86 Android tablet DSDT fixups. It covers Asus ME176C and TF103C tablets, adding missing charger, fuel gauge, sensors, touchscreen, USB-ID, lid switch, and optional Bluetooth serdev data.

Important APIs and data: exports `asus_me176c_info` and `asus_tf103c_info`. Shared data defines an `intel-int3496` platform device and gpio-keys lid switch software nodes. ME176C instantiates BQ24190/BQ24297 charger, UG3105 fuel gauge, AK09911 compass, KXTJ21009 accelerometer, Goodix touchscreen, and BCM serdev. TF103C instantiates similar charger/fuel-gauge/compass/accelerometer devices plus an Atmel touchscreen with GPIO IRQ.

State and dependencies: static software nodes and `x86_i2c_client_info` arrays are consumed during init by `core.c`. Dependencies include Bay Trail GPIO nodes, shared battery software nodes, charger platform data, I2C adapter paths, PMIC/APIC/GPIO IRQ helpers, serdev helpers, and gpio-keys.

Risks and test signals: board manifests are sensitive to I2C addresses, IRQ polarity, mount matrices, and battery chemistry selection. Tests should verify ME176C and TF103C DMI routes select the right info, all clients bind on expected adapters, lid switch reports `SW_LID`, charger/fuel gauge supply links resolve, and optional serdev binding does not block other devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/asus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/core.c

Purpose: runtime engine for DMI-based x86 Android tablet fixups. It selects a board manifest, registers required software nodes, instantiates missing I2C/SPI/serdev/platform devices, wires IRQs, and unwinds everything on removal.

Important APIs and control flow: `x86_android_tablet_init()` uses `platform_create_bundle()` so probe runs at module init. Probe DMI-matches `x86_android_tablet_ids`, preloads required modules, registers GPIO-chip and board software-node groups, calls optional board init, creates I2C/SPI/serdev/platform devices, and optionally adds a gpio-keys platform device. Helpers resolve GPIO descriptors before consumer devices exist, map APIC/GPIO/PMIC IRQs, find I2C adapters by ACPI handle or PCI parent, create SPI devices, and bind serdev ACPI nodes to chosen controllers.

State and persistence: global arrays track instantiated clients/devices and counts for reverse-order cleanup. `exit_handler` stores a board-specific cleanup callback. Software-node groups remain registered for the module lifetime and are unregistered on removal.

Dependencies and integration: depends on DMI table data, ACPI, GPIO lookup tables, IRQ domains, I2C/SPI/serdev/platform buses, PCI, software node APIs, and `serdev_helpers.h`.

Risks and test signals: this code runs from module init and cannot rely on normal deferred probing, so module preloading and probe ordering are important. Error unwinding spans many object types. Tests should cover each IRQ type, missing adapters/controllers, partial failure cleanup, gpio-button registration, module unload after all object types are created, and every DMI board manifest selected by `dmi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/dmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/dmi.c

Purpose: central DMI dispatch table for the x86 Android tablet fixup driver. It maps supported tablet DMI signatures to per-board `struct x86_dev_info` manifests defined in vendor files.

Important APIs and control flow: exports `x86_android_tablet_ids[]` and `MODULE_DEVICE_TABLE(dmi, ...)`. Entries include Acer, Advantech, Asus, Chuwi, Cyberbook, CZC/ViewSonic, Lenovo, Medion, Nextbook, Peaq, Vexia, Whitelabel, and Xiaomi devices. Many matches add BIOS date/version/SKU constraints where vendor/product strings are generic.

State and dependencies: no runtime state beyond the static table. It depends on extern `x86_dev_info` records from `acer.c`, `asus.c`, `lenovo.c`, and `other.c`, and is consumed by `dmi_first_match()` in `core.c`.

Risks and test signals: ordering is significant where generic matches could catch multiple tablets; comments call out cases like Lenovo Yoga Tablet 2 13-inch before 8/10-inch matches. Tests should verify modalias generation, DMI matching specificity, no accidental match broadening, and that every `driver_data` target is linked into the composite object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/dmi.c -->
