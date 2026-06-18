# subset-b-001023 Research

Grouped research for the listed ACPI files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/battery.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/battery.c

## Purpose
Implements the generic ACPI battery platform driver for PNP0C0A-compatible batteries and selected Microsoft Surface battery IDs. It translates ACPI control methods into the Linux `power_supply` class, reports battery presence, charge/energy/current/voltage/status properties, handles battery alarms, emits ACPI/netlink/power_supply notifications, and exposes a small hook API for platform-specific battery extensions.

## Important APIs, Types, And Functions
`struct acpi_battery` is the persistent per-battery state: ACPI device pointer, `power_supply_desc`, registered `power_supply`, update mutex, PM notifier, cached AML values, string fields, alarm, unit, and quirk flags. The ACPI ID table matches `PNP0C0A` and `MSHW0146`.

The main AML readers are `acpi_battery_get_status()` for `_STA`, `acpi_battery_get_info()` for `_BIX` or fallback `_BIF`, `acpi_battery_get_state()` for `_BST`, and `acpi_battery_set_alarm()` for `_BTP`. `extract_package()` maps integer/string package entries into `struct acpi_battery` using offset tables for `_BST`, `_BIF`, and `_BIX`.

`acpi_battery_get_property()` is the `power_supply` property callback. It exposes status, presence, technology, cycle count, voltage, current or power, full/design/current charge or energy, capacity percent, capacity level, model, manufacturer, and serial number. Separate property arrays are chosen for charge-mode versus energy-mode batteries and for broken full-capacity reporting.

Probe/remove entry points are `acpi_battery_probe()` and `acpi_battery_remove()` through the `acpi-battery` platform driver. Notifications are handled by `acpi_battery_notify()` installed via `acpi_dev_install_notify_handler()`. Sleep transitions use `acpi_battery_resume()` and a PM notifier `battery_notify()`.

The exported hook API is `battery_hook_register()`, `battery_hook_unregister()`, and `devm_battery_hook_register()`, backed by `acpi_battery_list`, `battery_hook_list`, and `hook_mutex`.

## Control Flow
Module init exits if ACPI is disabled or an AC/battery skip quirk applies, runs DMI quirks, then registers the platform driver. Probe obtains the ACPI companion, defers while dependencies are unmet, allocates state, detects `_BIX`, retries `acpi_battery_update()` up to five times, registers a PM notifier, enables wakeup, and installs the ACPI notify handler.

`acpi_battery_update()` first refreshes `_STA`. If the battery is absent, it unregisters the `power_supply` and clears the update cache. On first present update it reads `_BIX/_BIF`, initializes `_BTP`, reads `_BST`, applies firmware quirks, registers the `power_supply` if needed, and emits a PM wakeup event for critical or below-alarm capacity. Runtime property reads call `_BST` only when the battery is present and the `cache_time` jiffies window has expired.

ACPI notifications lock `update_lock`, optionally delay for broken firmware, refresh static info on info-change events, update runtime state, generate ACPI netlink and notifier-chain events, and call `power_supply_changed()` if the old and new `power_supply` objects are still present. Resume clears `update_time` and runs an update in resume mode so suspended-state changes are noticed without unnecessarily rebuilding sysfs.

## State And Persistence
State is in memory only. `update_time` caches `_BST` results for `cache_time` milliseconds. DMI callbacks set global quirk booleans for broken `_BIX`, notification delay, and AC-supply reporting. Per-battery quirk bits normalize percentage capacity, old ThinkPad mAh reporting, and degraded full-charge capacity. The `alarm` sysfs attribute stores the last requested threshold in `struct acpi_battery` and writes `_BTP` when the battery is present. Registered power supplies and hook-provided attributes persist until hot-remove, driver remove, or module exit.

## Dependencies And Integration Points
The driver depends on ACPICA evaluation helpers, ACPI platform-device enumeration, DMI, PM notifier/wakeup APIs, `power_supply`, sysfs attribute groups, and the ACPI bus notification wrappers in `bus.c`. It integrates with userspace through `/sys/class/power_supply/<BID>/` and an `alarm` attribute, with other kernel drivers through the exported battery hook API, and with suspend/resume through PM notifiers and wake events.

## Risks
Firmware package shape is a major risk: `_BIX/_BIF/_BST` type or length mismatches return errors or produce missing properties. Unit conversion quirks are model-specific and can regress capacity reporting if applied too broadly. `extract_package()` accepts integer values as short strings for string fields, which preserves legacy behavior but makes malformed firmware observable in user-visible strings. Notification timing is firmware-sensitive, hence the DMI delay quirk. The hook API must be used carefully because failed hook addition unregisters the hook from all batteries.

## Test Signals
Useful signals include successful probe logs, non-empty `power_supply` properties, correct `_BIX` fallback to `_BIF`, hotplug removal/readdition behavior, `power_supply_changed()` on ACPI battery events, low/critical wakeup events, suspend/resume state refresh, and DMI quirk coverage on affected hardware. Fault injection or AML emulation should cover malformed packages, absent batteries, broken full-capacity values, and `_BTP` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/bgrt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/bgrt.c

## Purpose
Publishes the ACPI Boot Graphics Resource Table (BGRT) through sysfs. It lets userspace inspect firmware-provided boot-logo metadata and read the boot image bytes under the firmware ACPI kobject.

## Important APIs, Types, And Functions
`acpi_parse_bgrt()` is the ACPI table parser hook; it delegates to `efi_bgrt_init()` to populate the global EFI BGRT state. `bgrt_init()` is a `device_initcall` that maps the image memory and creates the sysfs group. The `BGRT_SHOW()` macro defines read-only attributes for `version`, `status`, `type`, `xoffset`, and `yoffset`. `BIN_ATTR_SIMPLE_RO(image)` exposes the mapped image as a binary sysfs attribute.

## Control Flow
Table parsing runs during ACPI table discovery and initializes `bgrt_tab` and `bgrt_image_size`. Later, `bgrt_init()` exits with `-ENODEV` if no image address exists. Otherwise it `memremap()`s the image, stores the pointer and size in `bin_attr_image`, creates `/sys/firmware/acpi/bgrt` below `acpi_kobj`, and attaches the attribute group. Errors unwind the kobject and memory mapping.

## State And Persistence
The only persistent runtime state is `bgrt_image`, `bgrt_kobj`, and the global BGRT metadata from EFI helpers. The mapped image remains available for the lifetime of the sysfs object; there is no explicit module exit path because this is built as core firmware support.

## Dependencies And Integration Points
Depends on `linux/efi-bgrt.h`, sysfs kobjects, `memremap()`, and the ACPI firmware kobject exported by `bus.c`. Userspace consumes the metadata and binary image under `/sys/firmware/acpi/bgrt`.

## Risks
Incorrect firmware image addresses or sizes can make `memremap()` fail or expose invalid data. The file assumes `acpi_kobj` exists by device init time. Since the binary attribute directly exposes firmware memory contents, bounds correctness in `bgrt_image_size` is important.

## Test Signals
Presence of `/sys/firmware/acpi/bgrt/{version,status,type,xoffset,yoffset,image}` on BGRT-capable EFI systems, successful image reads of exactly `bgrt_image_size`, and clean absence on systems with no BGRT are the main signals. Error-path testing should force mapping or sysfs creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/bgrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/bus.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/bus.c

## Purpose
Provides the ACPI core bus implementation and much of ACPI subsystem initialization. It evaluates device status, attaches private data to ACPI handles, negotiates `_OSC` capabilities, dispatches ACPI notifications, matches ACPI devices to drivers, registers the `acpi` bus type, and orders early/late ACPI boot setup.

## Important APIs, Types, And Functions
Global exports include `acpi_root`, `acpi_root_dir`, `acpi_kobj`, `acpi_bus_type`, and capability flags such as `osc_pc_lpi_support_confirmed`, `osc_cpc_flexible_adr_space_confirmed`, `osc_sb_native_usb4_support_confirmed`, and `osc_sb_native_usb4_control`.

Device status helpers are `acpi_bus_get_status_handle()` and `acpi_bus_get_status()`. Private data helpers wrap ACPICA attach/get/detach data with `acpi_bus_private_data_handler()`. `_OSC` support is implemented by `acpi_eval_osc()`, `acpi_osc_error_check()`, exported `acpi_run_osc()`, and `acpi_osc_handshake()`. Platform and USB4 negotiation are driven by `acpi_bus_osc_negotiate_platform_control()` and `acpi_bus_osc_negotiate_usb_control()`.

Notification support includes root `acpi_bus_notify()`, per-driver notify installation/removal, exported `acpi_dev_install_notify_handler()` and `acpi_dev_remove_notify_handler()`, and special `\_SB` shutdown handling through `acpi_sb_notify()`. Matching APIs include `acpi_companion_match()`, `acpi_set_modalias()`, `acpi_match_acpi_device()`, `acpi_match_device()`, `acpi_device_get_match_data()`, `acpi_match_device_ids()`, and `acpi_driver_match_device()`.

Driver/bus glue is `__acpi_bus_register_driver()`, `acpi_bus_unregister_driver()`, `acpi_bus_match()`, `acpi_device_probe()`, `acpi_device_remove()`, and child walkers `acpi_bus_for_each_dev()`, `acpi_dev_for_each_child()`, and `acpi_dev_for_each_child_reverse()`. Initialization entry points are `acpi_early_init()`, `acpi_subsystem_init()`, internal `acpi_bus_init()`, and `acpi_init()` registered with `subsys_initcall`.

## Control Flow
Early boot calls `acpi_early_init()` if ACPI is enabled. It enables ACPICA interpreter slack unless strict mode is set, makes ACPI mappings permanent, applies x86 DSDT copy DMI quirks, reallocates the root table, initializes ACPICA, and adjusts SCI routing on x86. `acpi_subsystem_init()` later enables ACPI mode and tells the regulator core firmware constraints are complete.

`acpi_init()` creates `/sys/firmware/acpi`, initializes PRMT and PCC, calls `acpi_bus_init()`, then runs architecture and feature initializers such as FFH, PCI MCFG, VIOT, HEST/GHES, scan, EC, debugfs, sleep proc, wakeup devices, debugger, `\_SB` notifications, and VIOT. `acpi_bus_init()` loads tables, probes ECDT EC, starts the interpreter, initializes AML objects, negotiates `_OSC`, installs table handlers, initializes sysfs and processor control, probes DSDT EC, initializes sleep and interrupt routing, installs root system notifications, creates `/proc/acpi`, and registers `acpi_bus_type`.

Runtime device binding flows through the generic driver core: `acpi_bus_match()` checks `match_driver` and ACPI IDs; `acpi_device_probe()` calls the ACPI driver's `ops.add`, installs a notify handler if provided, and takes a device reference; `acpi_device_remove()` removes notification handlers, invokes `ops.remove`, clears driver data, and drops the reference.

## State And Persistence
The file maintains global boot and negotiation state, proc/sysfs roots, and exported `_OSC` capability booleans consumed by other subsystems. ACPI devices keep status bits in `struct acpi_device`, private handle data in ACPICA, physical-node relationships protected by `physical_node_lock`, and driver binding state in the device core. There is no runtime persistence across boots.

## Dependencies And Integration Points
This file is the ACPI integration center. It depends on ACPICA table/interpreter/event APIs, Linux device core, procfs, sysfs kobjects, DMI on x86, regulator constraints, workqueues, reboot, PCI, APEI/GHES, PRMT, PCC, VIOT, EC, scan, sleep, debugfs, and architecture hooks. Its exported matching, registration, notification, and `_OSC` symbols are consumed by ACPI drivers and by non-ACPI buses using ACPI companions.

## Risks
Initialization order is delicate: EC, `_OSC`, table handlers, sysfs, scan, IRQ model, and notification setup all have firmware-ordering constraints. `_OSC` error handling must distinguish query failures from masked capabilities or downstream subsystems will assume unsupported features. Matching must avoid binding absent devices and avoid double-matching secondary physical devices sharing one ACPI companion. The graceful shutdown work function intentionally loops while reporting `_OST`, so it must only be scheduled for the specific shutdown notification.

## Test Signals
Boot logs for ACPICA revision, interpreter enablement, `_OSC` support/control masks, interrupt routing model, and absence of ACPI termination are primary signals. Driver binding/unbinding, ACPI modalias uevents, hotplug notifications with `_OST`, USB4/CPPC capability flags, and `/proc/acpi` plus `/sys/firmware/acpi` creation test the major paths. Firmware tables with malformed `_OSC`, missing `_STA`, shared companions, and hotplug events are important regression cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/button.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/button.c

## Purpose
Implements the ACPI power button, sleep button, and lid switch driver. It converts fixed ACPI button events and ACPI device notifications into Linux input events, exposes legacy lid state through procfs, handles wakeup signaling, and works around platforms with unreliable lid state reporting.

## Important APIs, Types, And Functions
`struct acpi_button` holds the ACPI companion, platform device, button type, input device, physical path string, press count, lid state tracking, suspend flag, and lid initialization flag. The driver matches lid, sleep, sleep fixed, power, and power fixed ACPI HIDs.

Lid state helpers are `acpi_lid_evaluate_state()` for `_LID`, `acpi_lid_notify_state()` for SW_LID input events and firmware workaround logic, `acpi_lid_update_state()`, and `acpi_lid_initialize_state()`. Exported `acpi_lid_open()` lets graphics and platform drivers query the current lid state.

Notification handlers are `acpi_lid_notify()` for lid status events, `acpi_button_notify()` for power/sleep key events, and `acpi_button_event()` for fixed ACPI events. Procfs helpers create `/proc/acpi/button/lid/<BID>/state`. Module parameters are `lid_report_interval` and `lid_init_state`.

## Control Flow
Module init chooses `lid_init_state` from the explicit module parameter, DMI quirks, or default method-based initialization. It returns success without registering the platform driver when ACPI is disabled so modules linked against `acpi_lid_open()` can still load.

Probe identifies the button type from HID, rejects lid devices disabled by quirks, allocates state and an input device, creates legacy procfs state for lids, sets input capabilities (`KEY_POWER`, `KEY_WAKEUP`, `KEY_SLEEP`, or `SW_LID`), registers the input device, enables wakeup, then installs either a fixed event handler or an ACPI notify handler. Lid input open and resume initialize the switch state. Remove unregisters the corresponding ACPI event handler, waits for ACPI events to drain, disables wakeup, removes procfs, unregisters input, and frees state.

Button notifications generate PM wakeup events. While suspended, or for explicit wake notifications, they do not emit key presses. Normal power/sleep notifications synthesize key press/release pairs and generate ACPI netlink events. Lid notifications ignore events until initialization completes, evaluate `_LID`, optionally wake the system on open, and update SW_LID with workaround logic for platforms that miss open events or report bad initial state.

## State And Persistence
Global state includes `lid_device`, `lid_init_state`, `acpi_button_dir`, and `acpi_lid_dir`. Per-button state tracks `last_state`, `last_time`, `pushed`, `suspended`, and `lid_state_initialized`. Procfs nodes and input devices persist while the driver is bound. There is no on-disk state.

## Dependencies And Integration Points
Depends on ACPI fixed events and device notifications, platform-device ACPI matching, the input subsystem, procfs, DMI, PM wakeup helpers, and ACPI netlink event generation. `acpi_lid_open()` is an exported integration point for display drivers and platform code that need lid state.

## Risks
Lid firmware is historically unreliable. The complement-event logic avoids lost close events but can create surprising event sequences if applied to a reliable machine, so DMI and module-parameter behavior matter. The code assumes at most one meaningful lid procfs directory and reports an error on multiple lids. Fixed event and notify handler removal must match the handler type installed at probe. Input events are suppressed during suspend to avoid duplicate wake and key events.

## Test Signals
Signals include correct `/dev/input` events for power/sleep/lid, correct `/proc/acpi/button/lid/*/state`, wake events on button/lid activity, no key press on wake-only notifications, correct behavior after suspend/resume, and DMI quirk behavior on listed machines. Regression testing should include fixed-button devices, normal notify devices, disabled lid quirk systems, and unreliable `_LID` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/button.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/container.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/container.c

## Purpose
Registers ACPI generic container devices and wires them into Linux container hotplug handling. Containers represent hotpluggable physical groupings such as chassis, docks, or processor/memory containers, depending on firmware.

## Important APIs, Types, And Functions
The handler matches `ACPI0004`, `PNP0A05`, and `PNP0A06`. With `CONFIG_ACPI_CONTAINER`, `container_device_attach()` creates a `struct container_dev` and registers a device on `container_subsys`; `acpi_container_offline()` verifies that all dependent child devices are offline; `container_device_detach()` unregisters the container; and `container_device_online()` emits `KOBJ_ONLINE`. Without `CONFIG_ACPI_CONTAINER`, only a scan handler with hotplug name `"container"` is registered.

## Control Flow
`acpi_container_init()` registers the scan handler during ACPI scan setup. In the full container configuration, attach ignores dock stations, allocates a `container_dev`, sets the ACPI companion, assigns release/offline callbacks, registers the device, and stores it in `adev->driver_data`. Hotplug configuration enables demand-offline and online notification. Detach clears driver data and unregisters the device.

## State And Persistence
State is per attached ACPI container: a dynamically allocated `container_dev` and a `driver_data` link from the ACPI device. Offline readiness is computed dynamically by walking ACPI children with `acpi_scan_is_offline()`.

## Dependencies And Integration Points
Depends on ACPI scan handlers, ACPI child iteration from `bus.c`, `linux/container.h`, the container subsystem bus, and ACPI hotplug. Dock integration is explicit: dock stations are skipped to avoid creating a generic container device for them.

## Risks
Incorrect offline decisions can block or allow unsafe hot-removal. The attach path returns `1` on successful attachment, matching ACPI scan-handler conventions; callers must preserve that semantic. The non-`CONFIG_ACPI_CONTAINER` path still registers hotplug handling, so behavior differs based on kernel configuration.

## Test Signals
Expected signals are container devices appearing under the container subsystem for matching ACPI IDs, hotplug demand-offline calls refusing busy children, online uevents after attach, and no generic container device for ACPI dock stations. Tests should cover both `CONFIG_ACPI_CONTAINER` enabled and disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/cppc_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/cppc_acpi.c

## Purpose
Implements the ACPI CPPC library used primarily by CPU frequency and scheduler-related code. It parses per-CPU `_CPC` and `_PSD` packages, maps CPPC registers across PCC, SystemMemory, SystemIO, and FFH address spaces, exposes read-only per-CPU CPPC sysfs data, and exports helpers for performance capabilities, feedback counters, desired performance, autonomous selection, EPP, performance limits, and perf/frequency conversion.

## Important APIs, Types, And Functions
`struct cppc_pcc_data` stores PCC channel state per subspace: mailbox channel, timing limits, ownership bits, pending write state, write counters, locks, wait queue, and reference count. `pcc_data[]` maps subspace IDs to that state; `cpu_pcc_subspace_idx` and `cpc_desc_ptr` are per-CPU. Each `struct cpc_desc` contains parsed CPC register resources, `_PSD` domain info, sysfs kobject, CPU ID, and RMW lock.

Probe and cleanup are exported as `acpi_cppc_processor_probe()` and `acpi_cppc_processor_exit()`. Domain helpers include `acpi_cpc_valid()`, `cppc_allow_fast_switch()`, and `acpi_get_psd_map()`. PCC helpers include `check_pcc_chan()`, `send_pcc_cmd()`, `register_pcc_channel()`, and `pcc_data_alloc()`.

Register access is centralized in `cpc_read()`, `cpc_write()`, `cppc_get_reg_val()`, and `cppc_set_reg_val()`, with PCC-specific wrappers that ring the doorbell. Architecture hooks `cpc_ffh_supported()`, `cpc_supported_by_cpu()`, `cpc_read_ffh()`, and `cpc_write_ffh()` are weak defaults for arch overrides.

Exported performance APIs include `cppc_get_desired_perf()`, `cppc_get_nominal_perf()`, `cppc_get_highest_perf()`, `cppc_get_epp_perf()`, `cppc_get_perf_caps()`, `cppc_get_perf_ctrs()`, `cppc_set_epp_perf()`, `cppc_set_epp()`, `cppc_get_auto_act_window()`, `cppc_set_auto_act_window()`, `cppc_get_auto_sel()`, `cppc_set_auto_sel()`, `cppc_set_enable()`, `cppc_get_perf()`, `cppc_set_perf()`, `cppc_get_perf_limited()`, `cppc_set_perf_limited()`, `cppc_get_transition_latency()`, `cppc_get_dmi_max_khz()`, `cppc_perf_to_khz()`, and `cppc_khz_to_perf()`.

## Control Flow
`acpi_cppc_processor_probe()` first requires CPPC v2 `_OSC` acknowledgement unless the CPU architecture reports native CPPC support. It evaluates `_CPC`, validates revision and entry count, allocates a descriptor, parses integer and register-buffer entries, validates address spaces, maps SystemMemory registers, records a single PCC subspace ID, marks unsupported future entries, parses `_PSD`, registers a PCC channel once per subspace, stores the per-CPU descriptor, and creates an `acpi_cppc` kobject under the CPU device.

Reads of PCC-backed register sets take the PCC write lock, send a read command to refresh shared memory, then read all registers. Writes to individual PCC-backed registers write shared memory and send a write command. `cppc_set_perf()` has a special two-phase algorithm: multiple CPUs take the PCC read lock to update their desired/min/max registers in parallel, mark a pending write, and then one CPU obtains the write lock and sends the batched PCC write command; others wait for `pcc_write_cnt` to advance.

SystemMemory writes use the per-descriptor raw spinlock for read-modify-write masking. SystemIO uses ACPICA port helpers. FFH delegates to arch hooks. Unknown address spaces fall back to ACPICA memory access when appropriate.

## State And Persistence
CPPC state is entirely in memory and per CPU or per PCC subspace. PCC subspace objects are reference counted across CPUs and freed when the last CPU exits. SystemMemory register mappings are ioremapped during probe and unmapped at exit. Per-CPU sysfs kobjects live under CPU devices while the descriptor is active. Static `max_khz` caches the DMI fallback frequency for perf/frequency conversion.

## Dependencies And Integration Points
Depends on ACPI processor objects, `_OSC` capability flags from `bus.c`, ACPICA package extraction, PCC mailbox channels, CPU topology/cpumasks, per-CPU storage, sysfs kobjects, DMI, IO port and MMIO helpers, weak arch FFH hooks, and cpufreq shared-policy semantics. It is consumed by CPPC cpufreq drivers and other CPU performance management code.

## Risks
Firmware parsing is strict and can reject malformed `_CPC`/`_PSD` packages. PCC ownership, MPAR/MRTT timing, and batched write concurrency are high-risk areas: missed wakeups or incorrect lock transitions can lose performance requests. Flexible address-space support is gated by `_OSC`; accepting SystemMemory/SystemIO without it can violate older ACPI contracts unless CPU native support is present. Register bit-width and offset masking must avoid corrupting adjacent fields. The DMI frequency fallback is intentionally crude and should only be used when firmware lacks frequency registers.

## Test Signals
Signals include successful per-CPU `acpi_cppc` sysfs directories, valid `cppc_get_perf_caps()` values, cpufreq policy creation, correct `_PSD` shared CPU masks, PCC command completion without timeout/error bits, fast-switch allowance only for SystemMemory/SystemIO desired registers, EPP/autonomous selection writes, performance-limited sticky-bit clearing, and CPU hotplug cleanup. Stress tests should target concurrent `cppc_set_perf()` on shared PCC subspaces, malformed firmware packages, unsupported address spaces, and MPAR/MRTT limit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/cppc_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/debugfs.c

## Purpose
Creates the top-level ACPI debugfs directory used by ACPI debug and diagnostic code.

## Important APIs, Types, And Functions
Exports `struct dentry *acpi_debugfs_dir` with `EXPORT_SYMBOL_GPL`. `acpi_debugfs_init()` creates the `"acpi"` directory at debugfs root using `debugfs_create_dir()`.

## Control Flow
`acpi_debugfs_init()` is called from ACPI core initialization in `bus.c` after ACPI scan and EC setup. It assigns the returned dentry to the exported global. There is no teardown path here.

## State And Persistence
The only state is the global debugfs dentry pointer. Debugfs contents are volatile and exist only while debugfs is mounted and the kernel is running.

## Dependencies And Integration Points
Depends on `CONFIG_DEBUG_FS` infrastructure through `linux/debugfs.h` and ACPI internal init ordering. Other ACPI components can create files beneath `acpi_debugfs_dir`.

## Risks
Callers must tolerate debugfs being unavailable or directory creation returning an error-like dentry depending on debugfs configuration. Because the symbol is global, consumers should avoid assuming init has run before ACPI core setup.

## Test Signals
On debugfs-enabled systems, `/sys/kernel/debug/acpi` should exist after ACPI initialization. Consumers creating child files under `acpi_debugfs_dir` provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/device_pm.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/device_pm.c

## Purpose
Provides ACPI device power-management primitives and the generic ACPI PM domain. It discovers and changes ACPI D-states, manages power resources, handles wakeup GPEs and wake power, installs PM notification handlers, chooses sleep/runtime target states, and attaches ACPI PM callbacks to devices with ACPI companions.

## Important APIs, Types, And Functions
State helpers include `acpi_power_state_string()`, `acpi_device_get_power()`, `acpi_device_set_power()`, `acpi_bus_set_power()`, `acpi_bus_init_power()`, `acpi_device_update_power()`, and `acpi_bus_update_power()`. Fixup helpers include `acpi_device_fix_up_power()`, `acpi_device_fix_up_power_extended()`, `acpi_device_fix_up_power_children()`, and `acpi_dev_power_up_children_with_adr()`.

Wakeup helpers include `acpi_pm_wakeup_event()`, `acpi_add_pm_notifier()`, `acpi_remove_pm_notifier()`, `acpi_bus_can_wakeup()`, `acpi_pm_device_can_wakeup()`, and `acpi_pm_set_device_wakeup()`. Sleep-state selection is handled by `acpi_dev_pm_get_state()` and exported `acpi_pm_device_sleep_state()`.

Runtime/system PM entry points include `acpi_dev_suspend()`, `acpi_dev_resume()`, `acpi_subsys_runtime_suspend()`, `acpi_subsys_runtime_resume()`, `acpi_subsys_prepare()`, `acpi_subsys_complete()`, `acpi_subsys_suspend()`, `acpi_subsys_suspend_late()`, `acpi_subsys_suspend_noirq()`, `acpi_subsys_freeze()`, `acpi_subsys_restore_early()`, and `acpi_subsys_poweroff()`. `acpi_dev_pm_attach()` and `acpi_dev_pm_detach()` manage the `acpi_general_pm_domain`. `acpi_storage_d3()` and `acpi_dev_state_d0()` are exported policy/query helpers.

## Control Flow
Power discovery combines power-resource inference with `_PSC` when available. Setting power validates state support and parent state, handles D3cold as `_PS3` plus power-resource removal, executes `_PSx` in ACPI 6 order, updates power resources, and records `device->power.state`. Initialization sets unknown state, skips absent devices, references active power resources, and defaults to D0 when firmware provides no readable state.

Wake notifications install an ACPI system notify handler that responds to `ACPI_NOTIFY_DEVICE_WAKE`, signals a wakeup source, and optionally runs a registered callback. Wake enablement acquires `acpi_wakeup_lock`, enables wake power, enables the GPE, and maintains `enable_count`; disable reverses those steps.

Runtime suspend runs generic runtime suspend and then ACPI low-power transition with wake enabled. Runtime resume powers to D0, disables wake, then runs generic resume. System sleep callbacks coordinate with smart suspend, runtime-suspended devices, wake settings, `_SxD/_SxW/_S0W`, PM QoS, firmware-resume expectations, and driver callback ordering. PM domain attach installs the wake notifier and assigns `acpi_general_pm_domain` only to the first physical node for a companion and skips special IDs such as ACPI fans.

## State And Persistence
Persistent runtime state lives in each `struct acpi_device`: `power.state`, valid power-state descriptors, power-resource flags, wakeup context, wake GPE, wakeup source, notifier flags, and enable counters. Global mutexes serialize notifier installation, notifier callbacks, and wake GPE/power operations. Device PM domain assignment persists until detach. There is no persistent storage.

## Dependencies And Integration Points
Depends on ACPI power-resource helpers, ACPICA `_PSC/_PSx/_SxD/_SxW/_S0W` evaluation, Linux PM core, runtime PM, PM QoS, wakeup sources, suspend-to-idle logic, ACPI companion relationships from the bus layer, ACPI fan special IDs, fwnode properties, and platform storage-D3 quirks.

## Risks
Incorrect D-state choice can break enumeration, runtime PM, wakeup, or resume. Parent/child power ordering and shared power resources make inferred state differ from actual device state. Wake enable counts must stay balanced across repeated suspend/resume paths. Firmware may power devices during system sleep, requiring resume correction. PM-domain attachment to secondary physical nodes sharing a companion would double-apply ACPI PM, so the first-node check is essential.

## Test Signals
Signals include correct `power_state` and `real_power_state` sysfs values, successful runtime suspend/resume through ACPI PM domain, wake GPE enable/disable logs, wake from device events, proper behavior with PM QoS `NO_POWER_OFF`, storage D3 policy detection, non-D0 probe checks, and no resume regressions after firmware-assisted sleep. Tests should cover devices with only `_PSx`, only power resources, both `_PSC` and resources, wake-capable `_PRW`, wake IRQs, and shared ACPI companions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/device_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/device_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/device_sysfs.c

## Purpose
Defines ACPI device sysfs attributes, modalias/uevent generation, eject handling, and exposure of ACPI non-device data subnodes. It is the main bridge between ACPI namespace metadata and userspace-visible device attributes.

## Important APIs, Types, And Functions
`acpi_object_path()` formats full ACPI paths. `struct acpi_data_node_attr`, `acpi_data_node_ktype`, `acpi_expose_nondev_subnodes()`, and `acpi_hide_nondev_subnodes()` expose and remove non-device ACPI data nodes recursively.

Modalias helpers are `create_pnp_modalias()`, `create_of_modalias()`, `__acpi_device_uevent_modalias()`, exported `acpi_device_uevent_modalias()`, `__acpi_device_modalias()`, and exported `acpi_device_modalias()`. Device attributes include `modalias`, `real_power_state`, `power_state`, `eject`, `hid`, `cid`, `uid`, `adr`, `path`, `description`, `sun`, `hrv`, and `status`. `acpi_attr_is_visible()` gates attributes dynamically. `acpi_groups` is the attribute-group array consumed by ACPI device registration.

## Control Flow
When device sysfs is built, the group visibility callback checks ACPI capabilities and PNP metadata before exposing each attribute. Reads evaluate ACPI methods such as `_STR`, `_SUN`, `_HRV`, and `_STA` on demand, or return cached PNP/power metadata. `eject_store()` accepts only `"1"`, verifies a hotplug handler or driver and `_EJ0` eligibility, takes an ACPI device reference, schedules ACPI hotplug eject, and reports `_OST` failure if scheduling fails.

Uevent modalias generation writes `MODALIAS=` and fills either ACPI PNP IDs (`acpi:HID:CID:`) or DT-compatible modalias strings for ACPI devices using `ACPI_DT_NAMESPACE_HID`. The sysfs `modalias` attribute can include both ACPI and OF-compatible forms. Non-device subnodes are added recursively as kobjects under the ACPI device kobject and removed in reverse order.

## State And Persistence
Most values are computed on read. Non-device subnode kobjects persist while the parent ACPI device is present and use completions to signal release. Hotplug eject temporarily holds an ACPI device reference until the scheduled hotplug path consumes it or failure releases it.

## Dependencies And Integration Points
Depends on ACPICA name/method/object-info APIs, Linux sysfs/kobject infrastructure, ACPI hotplug scheduling, ACPI PM helpers from `device_pm.c`, modalias matching from `bus.c`, UTF-16 to UTF-8 conversion for `_STR`, and fwnode/ACPI data-node structures. It integrates with userspace module loading through uevent modaliases.

## Risks
Modalias buffers must not overflow or truncate silently because they affect module autoload. Attribute visibility must match firmware support; exposing methods that fail frequently creates noisy user-visible errors. `eject_store()` must correctly handle references and `_OST` failure reporting or hotplug errors can leak references or leave firmware uninformed. Recursive data-node kobject removal must mirror creation order.

## Test Signals
Signals include correct sysfs attributes for devices with HID/CID/UID/ADR/_STR/_SUN/_HRV/_STA/_EJ0, correct uevent `MODALIAS`, module autoload for ACPI IDs, successful eject scheduling and failure `_OST`, valid UTF-8 descriptions, and correct recursive appearance/removal of non-device data nodes. Buffer-boundary tests for many CIDs and OF compatible strings are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/device_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dock.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/dock.c

## Purpose
Implements ACPI dock station and bay support. It tracks dock stations, dependent ACPI devices, dock/undock notifications, hotplug fixups, sysfs controls, and userspace dock/undock uevents.

## Important APIs, Types, And Functions
`struct dock_station` stores the ACPI handle, flags, last dock time, dependent device list, list node, and platform dock device. `struct dock_dependent_device` links dependent ACPI devices. Public helpers are `register_dock_dependent_device()`, exported `is_dock_device()`, `dock_notify()`, and `acpi_dock_add()`.

Dock operations include `dock_present()` for `_STA`, `handle_dock()` for `_DCK`, `dock()` and `undock()`, `handle_eject_request()` for removal, `hot_remove_dock_devices()` and `hotplug_dock_devices()` for dependent devices, and `dock_event()` for uevents and hotplug callbacks. Sysfs attributes are `docked`, `flags`, `undock`, `uid`, and `type`. The `immediate_undock` module parameter controls whether eject notifications undock immediately.

## Control Flow
`acpi_dock_add()` creates a `dock` platform device, initializes the station, classifies it as dock, ATA bay, or battery bay, creates sysfs attributes, adds the station as dependent on itself, links it globally, and marks the ACPI device as a dock station.

`dock_notify()` translates dock-station `DEVICE_CHECK` to eject when `_DCK` indicates a dock. On bus/device check for an unenumerated device, it begins docking, evaluates `_DCK(1)`, checks presence, runs dependent-device fixups and hotplug handlers, scans unenumerated dependents, completes docking, emits dock events, locks the dock with `_LCK(1)`, and updates GPEs. If a dock is no longer present, it treats the event as surprise removal. Eject requests begin undock and either call `handle_eject_request()` immediately or emit an undock event for userspace to trigger the `undock` sysfs write.

`handle_eject_request()` rejects active docking, emits the undock event before device removal, invokes dependent hot-remove handlers in reverse order, trims ACPI devices, evaluates `_DCK(0)`, unlocks with `_LCK(0)`, evaluates `_EJ0`, verifies absence, and completes undocking.

## State And Persistence
Global `dock_stations` and `dock_station_count` track registered stations. Per-station flags include docking/undocking in progress and type bits. `last_dock_time` suppresses false dock events shortly after docking. Dependent-device lists persist for the lifetime of the dock platform device. Sysfs `undock` writes drive state transitions; no state is stored across boots.

## Dependencies And Integration Points
Depends on ACPI scan/hotplug, ACPICA `_STA/_DCK/_LCK/_EJ0/_UID`, platform devices, sysfs, kobject uevents, ACPI hotplug callback structures, ACPI scan locking, and GPE update helpers. It integrates with other ACPI drivers through `register_dock_dependent_device()` and `is_dock_device()`.

## Risks
Docking hardware can emit duplicate or false events; `dock_in_progress()` and `last_dock_time` mitigate but can also suppress legitimate rapid transitions. Surprise removal must remove dependents in reverse order to respect dependencies. Immediate undock for ATA bays is disabled by default behavior because storage removal may need userspace coordination. Errors after `_EJ0` can leave firmware and kernel state partially changed.

## Test Signals
Signals include dock platform devices with correct sysfs files, dock/undock uevents, dependent device hotplug callbacks in expected order, ACPI bus scans for newly enumerated devices, safe sysfs-driven undock, surprise removal handling, and `_LCK/_EJ0/_DCK` method traces. Regression tests should include normal docks, ATA bays, battery bays, duplicate notifications, and failed undock presence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/dptf/Kconfig

## Purpose
Defines Kconfig options for Intel Dynamic Platform and Thermal Framework ACPI participants under `drivers/acpi/dptf`.

## Important APIs, Types, And Functions
`menuconfig ACPI_DPTF` enables the DPTF menu and depends on `X86`. `config DPTF_POWER` builds the platform power participant driver, defaulting to module. `config DPTF_PCH_FIVR` builds the PCH FIVR participant driver, also defaulting to module.

## Control Flow
Kconfig selection controls which objects the DPTF Makefile builds. `ACPI_DPTF` must be enabled before either child option is visible. The help text describes the participant responsibilities and module names.

## State And Persistence
This file contributes build-time configuration only. The selected values are persisted in the kernel `.config`, not in runtime state.

## Dependencies And Integration Points
Depends on the kernel Kconfig system and x86 ACPI platforms. It integrates with `drivers/acpi/dptf/Makefile`, which maps `CONFIG_DPTF_POWER` and `CONFIG_DPTF_PCH_FIVR` to object files.

## Risks
Defaulting both participant drivers to modules can change distribution build contents when `ACPI_DPTF` is enabled. The `X86` dependency prevents accidental exposure on unsupported architectures but also excludes any future non-x86 DPTF use until adjusted.

## Test Signals
Signals are Kconfig visibility under x86, correct module names in generated config/help, and expected object inclusion for built-in, module, and disabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/dptf/Makefile

## Purpose
Builds the DPTF ACPI participant drivers selected by Kconfig.

## Important APIs, Types, And Functions
The object mappings are `obj-$(CONFIG_DPTF_POWER) += dptf_power.o` and `obj-$(CONFIG_DPTF_PCH_FIVR) += dptf_pch_fivr.o`.

## Control Flow
Kbuild expands each `obj-*` line according to the corresponding configuration value. Built-in selections compile into the kernel image, module selections produce loadable modules, and disabled selections omit the object.

## State And Persistence
No runtime state. Build output depends entirely on `.config`.

## Dependencies And Integration Points
Depends on Kbuild and the Kconfig symbols from the sibling `Kconfig`. It is included by the parent ACPI drivers Makefile.

## Risks
The file is simple; risk is limited to symbol/object drift if source files or Kconfig option names are renamed.

## Test Signals
Build tests should verify `dptf_power.o` and `dptf_pch_fivr.o` are produced for built-in/module configurations and absent when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_pch_fivr.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_pch_fivr.c

## Purpose
Implements the Intel DPTF PCH FIVR participant driver. It exposes PCH Fully Integrated Voltage Regulator switching-frequency telemetry and controls through a sysfs attribute group for supported INTC10xx ACPI devices.

## Important APIs, Types, And Functions
`struct pch_fivr_resp` represents two-integer AML method responses: status and result. `pch_fivr_read()` evaluates a method, extracts a two-integer package, and succeeds only when the returned status is zero. `PCH_FIVR_SHOW()` defines read attributes backed by AML methods `GFC0`, `GFC1`, `GEMI`, `GFCS`, and `GFFS`. `PCH_FIVR_STORE()` defines write attributes backed by `RFC0` and `RFC1`.

The sysfs group `pch_fivr_switch_frequency` contains `freq_mhz_low_clock`, `freq_mhz_high_clock`, `ssc_clock_info`, `fivr_switching_freq_mhz`, and `fivr_switching_fault_status`. Probe/remove are `pch_fivr_add()` and `pch_fivr_remove()` in a platform driver matching several `INTC` ACPI IDs.

## Control Flow
Probe gets the ACPI companion, evaluates `PTYP`, and binds only participant type `0x05`. It creates the sysfs group and stores the ACPI device as platform driver data. Reads call the relevant `G*` method and print the result. Writes parse an unsigned integer and execute the relevant `R*` method. Remove deletes the sysfs group.

## State And Persistence
The driver stores only the ACPI device pointer in platform driver data. FIVR settings and telemetry live in firmware/platform hardware and are accessed on demand through AML methods.

## Dependencies And Integration Points
Depends on ACPI platform-device enumeration, AML method evaluation/extraction, sysfs groups, and DPTF firmware participant semantics. It integrates with user-space thermal/power policy daemons through `/sys/.../pch_fivr_switch_frequency/`.

## Risks
The driver trusts participant type to distinguish the correct function among shared INTC IDs. AML response packages that are not exactly two numeric values or that report nonzero status return `-EFAULT`. Writes accept any `u32` and rely on firmware to validate the frequency request. `sprintf()` is used instead of `sysfs_emit()`, though outputs are small.

## Test Signals
Signals include binding only to `PTYP == 0x05`, presence of the sysfs group, successful reads of all telemetry attributes, successful writes to low/high clock controls with firmware-visible effects, and clean group removal on unbind. Negative tests should cover missing ACPI companion, wrong `PTYP`, malformed method packages, and failed AML writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_pch_fivr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_power.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_power.c

## Purpose
Implements Intel DPTF platform power and battery participant support. It exposes platform power-source/limit/adapter telemetry and DPTF battery electrical telemetry through sysfs, and notifies userspace when firmware reports changed values.

## Important APIs, Types, And Functions
`DPTF_POWER_SHOW()` defines read-only sysfs attributes backed by ACPI integer methods: `PMAX`, `PSRC`, `ARTG`, `PBSS`, `CTYP`, `PROP`, `RBHF`, `VBNL`, and `CMPP`. `prochot_confirm_store()` writes a sequence number to `PBOK`. `dptf_participant_type()` reads `PTYP`.

Two attribute groups exist: `dptf_power` for platform participant type `0x11`, and `dptf_battery` for battery participant type `0x0C`. `dptf_power_notify()` maps ACPI notification codes to changed attribute names and calls `sysfs_notify()`. Probe/remove are `dptf_power_add()` and `dptf_power_remove()` in a platform driver matching `INT3407`, `INT3532`, and multiple newer `INTC` IDs.

## Control Flow
Probe obtains the ACPI companion, reads `PTYP`, chooses the matching attribute group, installs an ACPI device notify handler, creates the sysfs group, and stores the ACPI device in platform data. Reads evaluate AML methods on demand and print integer values. `prochot_confirm` writes `PBOK`. Notifications for power source, power properties, max power, steady-state power, impedance, and voltage/current choose the relevant attribute and notify either the `dptf_battery` or `dptf_power` group based on current `PTYP`. Remove unregisters the notify handler and removes the appropriate sysfs group.

## State And Persistence
The driver keeps only the ACPI device pointer as platform data. All telemetry and control state is firmware-owned and read or written through AML methods. Sysfs notifications are transient events for userspace pollers.

## Dependencies And Integration Points
Depends on ACPI platform-device binding, AML integer method evaluation, ACPI notify handlers, sysfs groups/notifications, and DPTF participant firmware. It integrates with userspace thermal/power managers through `dptf_power` and `dptf_battery` sysfs directories.

## Risks
Participant type determines the sysfs ABI; firmware reporting an unexpected or changing `PTYP` can prevent binding or remove the wrong group. Notification mapping covers only known event codes and logs unsupported events. Attributes return `-EINVAL` on AML failure, so transient firmware errors surface directly to userspace. The attribute name `current_discharge_capbility_ma` preserves a misspelling, which is ABI once exposed.

## Test Signals
Signals include correct binding for `PTYP` `0x11` and `0x0C`, correct sysfs group selection, valid reads for all AML-backed attributes, successful `PBOK` writes, `sysfs_notify()` wakeups on supported ACPI events, and clean unbind. Negative tests should cover wrong `PTYP`, failed methods, unsupported notifications, and notification routing for battery versus platform participants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_power.c -->
