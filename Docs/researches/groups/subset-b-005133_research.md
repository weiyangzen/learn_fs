# subset-b-005133 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-tf103c-dock.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-tf103c-dock.c

## Purpose
`asus-tf103c-dock.c` is an I2C platform driver for the Asus TF103C keyboard dock. The dock has a private embedded controller plus separate I2C addresses for keyboard reports, interrupt status, EC command RAM, and an Elan touchpad, so the driver reconstructs normal Linux HID/input/touchpad behavior from nonstandard firmware protocols.

## Important APIs, Types, And Functions
The central state object is `struct tf103c_dock_data`, which owns the EC, interrupt, keyboard, and touchpad `i2c_client`s, GPIOs, IRQs, a delayed HPD work item, a synthetic HID keyboard, an input device for special top-row keys, touchpad nested IRQ plumbing, and runtime flags such as `enabled`, `tp_enabled`, `altgr_pressed`, and `fnlock` state. Probe binds only on TF103C DMI systems even though the ACPI ID is generic `NPCE69A`.

The keyboard path is split between `tf103c_dock_kbd_read()`, `tf103c_dock_kbd_write()`, a small `hid_ll_driver`, and `tf103c_dock_kbd_interrupt()`. Report ID `0x11` is forwarded as reconstructed keyboard HID, while report IDs `0x13`, `0x14`, and selected SCI events are mapped to top-row keys through `tf103c_dock_toprow_event()`. `tf103c_dock_report_toprow_kbd_hook()` strips Right Alt from normal HID reports and uses it as an Fn modifier; AltGr+Esc toggles the module-global `fnlock`.

The touchpad path creates an `elan_i2c` client dynamically in `tf103c_dock_enable_touchpad()`, using a software node to advertise `elan,clickpad`, and routes EC touchpad interrupts through a single-entry irqdomain using `handle_nested_irq()`. EC command helpers include `tf103c_dock_ec_cmd()`, `tf103c_dock_sci()`, and `tf103c_dock_smi()`.

## Control Flow
`tf103c_dock_probe()` installs GPIO lookups, reads the board revision, requests HPD and dock IRQs with `IRQF_NO_AUTOEN`, creates the extra I2C clients, registers the top-row input device and synthetic HID keyboard, creates a nested IRQ for the touchpad, and starts HPD polling through delayed work. HPD transitions call `tf103c_dock_enable()` or `tf103c_dock_disable()`: enable powers the dock on non-revision-2 boards, waits 500 ms, and enables the main EC IRQ; disable disables the IRQ, unregisters the touchpad, and drops power.

The threaded dock IRQ reads eight bytes from the interrupt client. Out-of-band report markers dispatch to either the nested touchpad IRQ or keyboard report handling. SCI bits trigger top-row multimedia events; SMI bits re-enable the EC/USB/keyboard after EC wake or instantiate the touchpad after HID status changes.

Suspend stops HPD handling and, if the dock is enabled, writes a suspend EC command and optionally enables wake on the dock IRQ. Resume disables wake, conditionally sends an enable command if HPD still says the dock is connected, and restarts HPD synchronization.

## State And Persistence
Most state is runtime-only in `struct tf103c_dock_data`. The exception is the module parameter `fnlock`, which can be set at load time or toggled at runtime through AltGr+Esc and affects top-row key interpretation. Device presence is not persisted; the touchpad client is recreated on dock/HID status changes and unregistered on dock removal or power-off. Board revision influences power GPIO behavior for the lifetime of the probe.

## Dependencies And Integration Points
The driver depends on ACPI/I2C enumeration, DMI matching, GPIO lookup tables for hardcoded Intel/Crystal Cove GPIOs, Linux HID core, input core, irqdomain/nested IRQ support, and the `elan_i2c` touchpad driver. It integrates with system suspend through `SIMPLE_DEV_PM_OPS` and with wakeup through `device_init_wakeup()`.

## Risks
The driver is highly board-specific despite matching a broad ACPI HID, so the DMI guard is essential. Firmware packet formats are inferred and only partially recognized; unknown keyboard or EC interrupt data is logged and ignored. Incorrect HPD, IRQ, or board-revision GPIO mappings can leave the dock powered incorrectly or make the EC unresponsive. The module-global `fnlock` is shared rather than per-device, which is acceptable for the single supported model but would not generalize.

## Test Signals
Useful validation includes TF103C boot/probe logs, HPD plug/unplug cycles, keyboard HID input including six-key boot reports, top-row multimedia/F1-F12 behavior with AltGr and `fnlock`, AltGr+Esc filtering, touchpad creation and nested IRQ delivery to `elan_i2c`, suspend/resume with dock attached and detached, wake from dock IRQ, and regression checks that unknown EC packets do not crash the threaded IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-tf103c-dock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wireless.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wireless.c

## Purpose
`asus-wireless.c` is a small ACPI platform driver for Asus wireless radio control devices with ACPI IDs `ATK4001` and `ATK4002`. It exposes the airplane/radio hotkey as an input event and, where supported, exposes the firmware radio LED through the LED class.

## Important APIs, Types, And Functions
`struct hswc_params` describes the firmware-specific values passed to the `HSWC` ACPI method for on, off, and status operations. `struct asus_wireless_data` stores the ACPI companion, input device, LED class device, single-thread workqueue, pending LED state, and selected HSWC parameters.

`asus_wireless_method()` wraps `acpi_evaluate_integer()` with a single integer parameter. `led_state_get()`, `led_state_set()`, and `led_state_update()` implement the LED class callbacks and defer writes to the workqueue. `asus_wireless_notify()` handles ACPI notify event `0x88` by emitting a press/release pair for `KEY_RFKILL`.

## Control Flow
Probe allocates driver data, registers an input device named `Asus Wireless Radio Control`, and sets it up for `KEY_RFKILL`. It then matches the ACPI ID to HSWC parameter data. If parameters exist, it creates a workqueue, initializes the airplane LED, registers the LED class device, and installs an ACPI device notify handler. Remove unregisters the notify handler, LED class device, and workqueue.

## State And Persistence
The only mutable state is `led_state`, a queued firmware command value. The actual radio/LED state lives in firmware and is read with `HSWC status`. There is no persistent kernel configuration and no sysfs-specific state beyond the LED class device.

## Dependencies And Integration Points
The driver integrates with ACPI platform devices, the Linux input subsystem, LED class, and default rfkill LED triggers. It intentionally overlaps with Asus WMI radio handling but targets the ASHS/ATK400x ACPI device path, and `asus-wmi.c` checks for these IDs to avoid conflicting rfkill ownership in some cases.

## Risks
Only ACPI event `0x88` is understood; other events are logged as unknown. LED writes are asynchronous, so rapid userspace writes collapse to the last queued `led_state`. Probe registers the input device before HSWC parameter matching, meaning unmatched variants still get hotkey reporting but no LED control.

## Test Signals
Test by loading on ATK4001 and ATK4002 systems, confirming `KEY_RFKILL` events on firmware notification `0x88`, validating LED brightness get/set maps to the right HSWC values for both ID variants, checking suspend/resume LED behavior through `LED_CORE_SUSPENDRESUME`, and verifying remove cancels firmware notification delivery and destroys the workqueue cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wireless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c

## Purpose
`asus-wmi.c` is the generic Asus WMI hotkey and platform-feature core. It provides shared WMI method wrappers and the lifecycle implementation used by model-specific Asus WMI frontends, then exposes firmware features through input, LED, rfkill, hwmon, power-supply, backlight, platform profile, sysfs, debugfs, and suspend hooks.

## Important APIs, Types, And Functions
The central state object is `struct asus_wmi`. It stores WMI method selection (`dsts_id`, `spec`, `sfun`), the registered input device, backlight devices, platform device, LED class devices and LED workqueue, rfkill objects, fan and fan-curve state, GPU/eGPU/MUX tunable capability flags, platform-profile state, battery charge threshold availability, debugfs fields, hotplug locks/workqueues, Fn-lock state, and the model-specific `struct asus_wmi_driver`.

The exported WMI API is `asus_wmi_evaluate_method()`, `asus_wmi_get_devstate_dsts()`, and `asus_wmi_set_devstate()` in the `ASUS_WMI` namespace. The file also exports HID coordination functions `asus_hid_register_listener()`, `asus_hid_unregister_listener()`, `asus_hid_event()`, `set_ally_mcu_hack()`, and `set_ally_mcu_powersave()`. Internally, `asus_wmi_evaluate_method3()`, `asus_wmi_evaluate_method5()`, `asus_wmi_evaluate_method_buf()`, and `asus_wmi_evaluate_method_agfn()` handle integer, buffer, five-argument, and DMA-address AGFN calls.

Major subsystem initializers include `asus_wmi_platform_init()`, `asus_wmi_input_init()`, `asus_wmi_led_init()`, `asus_wmi_rfkill_init()`, `asus_wmi_fan_init()`, `asus_wmi_hwmon_init()`, `asus_wmi_custom_fan_curve_init()`, `platform_profile_setup()`, `asus_wmi_backlight_init()`, `asus_screenpad_init()`, `asus_wmi_battery_init()`, `asus_wmi_sysfs_init()`, and `asus_wmi_debugfs_init()`.

## Control Flow
External model drivers call `asus_wmi_register_driver()`, which creates a bundled platform device/driver. `asus_wmi_probe()` verifies the management and event GUIDs, runs any model probe, registers Ally s2idle hooks, and calls `asus_wmi_add()`. Add allocates `struct asus_wmi`, runs model quirk detection, initializes WMI method selection based on WMI ACPI UID (`ASUSWMI` uses DCTS, others use DSTS), applies default feature discovery, then registers sysfs, input, hwmon, custom fan curves, LEDs, rfkill, backlight/screenpad, WMI notifications, optional i8042 filtering, battery hooks, and debugfs.

Runtime WMI events enter `asus_wmi_notify()`, are decoded by `asus_wmi_get_event_code()`, and are handled by `asus_wmi_handle_event_code()`. The handler applies model key filters, handles vendor backlight events if firmware backlight is active, handles keyboard backlight hotkeys, toggles Fn-lock, refreshes tablet mode, cycles fan/platform profiles for selected keys, suppresses known bad display-toggle events, and otherwise reports sparse-keymap events.

Remove unwinds notification, filters, backlights, screenpad, input, LEDs, rfkill, debugfs, sysfs, fan auto mode, platform thermal policy defaulting, battery hook, and state allocation. PM callbacks restore rfkill/hotplug, keyboard LED, Fn-lock, tablet mode, OOBE state, and Ally ACPI CSEE power sequencing.

## State And Persistence
Most kernel state is a cache or policy layer over firmware WMI state. Cached values include keyboard LED brightness, fan PWM modes, AGFN PWM value, fan boost mode, thermal policy mode, custom fan curves, platform-profile registration, battery RSOC availability, `charge_end_threshold`, and tunable defaults for deprecated sysfs attributes. Some settings are written to firmware and can survive until power cycle or firmware reset, while others are restored on resume or reset to automatic/default on driver removal.

Concurrency-sensitive LED/HID state is shared through the global `asus_ref` with a spinlock because HID callbacks can arrive in IRQ context. WMI/rfkill hotplug is protected by `wmi_lock` and `hotplug_lock`. The global `used` flag and `register_mutex` enforce one active Asus WMI driver instance.

## Dependencies And Integration Points
The file depends on ACPI WMI, ACPI video/backlight selection, input sparse keymaps, LED class, rfkill, PCI hotplug/rescan, platform profile, power supply battery hooks, hwmon, debugfs, i8042 filters, DMI, and optional suspend LPS0 hooks. It includes the public platform data header `<linux/platform_data/x86/asus-wmi.h>` for WMI device IDs and local `asus-wmi.h` for model-driver registration structures. It also coordinates with `hid-asus` through exported listener/event APIs and with `asus-wireless.c` by detecting ASHS devices to avoid duplicate wireless handling.

## Risks
The driver has a large firmware surface with many model-specific return conventions; unsupported methods can return ACPI failure, `ASUS_WMI_UNSUPPORTED_METHOD`, absent presence bits, no buffer, or odd success codes. Many sysfs attributes are visibility-gated by live WMI calls, so firmware latency or side effects can affect enumeration. Fan control and custom curves can affect thermals, so the code resets curves on mode changes and returns to automatic/default modes during removal. GPU/eGPU/MUX operations have interlocks but still rely on firmware semantics. Error unwinding is complex and has ordering sensitivity, especially around backlight/screenpad labels, LED registration, rfkill hotplug, and `devm` resources.

## Test Signals
Coverage should include registration by an Asus model driver, WMI GUID absence handling, DSTS/DCTS selection, input hotkey reporting, brightness hotkeys under vendor backlight mode, keyboard LED changes from both WMI and `hid-asus`, rfkill registration and PCI hotplug on older WLAN devices, hwmon fan/temp visibility, custom fan curve visibility and enable/reset behavior, platform-profile get/set/cycle, battery charge threshold attribute on BAT0/BAT1/BATC/BATT, debugfs calls, deprecated sysfs visibility, suspend/thaw/restore/resume paths, Ally CSEE power sequencing, and unload restoring fan/thermal policy defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.h

## Purpose
`asus-wmi.h` is the local private interface between the generic Asus WMI core and model-specific platform drivers in the same driver family. It defines quirk flags, key-filter hooks, and the `asus_wmi_driver` registration contract implemented by `asus-wmi.c`.

## Important APIs, Types, And Functions
`enum asus_wmi_tablet_switch_mode` identifies which WMI device/event pair should be used for tablet mode reporting. `struct quirk_entry` holds model behavior switches such as wireless hotplug support, scalar brightness, stored backlight power, forced ALS enabling, ignored fan support, i8042 filtering, display-toggle suppression, WAPF behavior, and USB port remapping.

`struct asus_wmi_driver` is the main model-driver descriptor. It carries mutable cached fields for brightness/panel/screenpad/wireless ownership, static identity strings, the event GUID, sparse keymap, input naming, quirk pointer, optional WMI key filter, optional i8042 filter, optional model probe and quirk detection callbacks, and the embedded `platform_driver`/`platform_device` used by the core. The exported functions are `asus_wmi_register_driver()` and `asus_wmi_unregister_driver()`.

## Control Flow
Model drivers populate `struct asus_wmi_driver` and call `asus_wmi_register_driver()`. The core fills in platform driver callbacks, creates the platform bundle, and later calls the model callbacks during probe. On unload, the model calls `asus_wmi_unregister_driver()` to unregister the platform device/driver pair.

## State And Persistence
The header itself stores no state, but its structures define which state is shared between model frontends and the core. `quirk_entry` is effectively static policy. The mutable fields in `asus_wmi_driver` are runtime caches used by backlight, screenpad, and wireless-control logic.

## Dependencies And Integration Points
It depends on `linux/platform_device.h` and `linux/i8042.h`, plus forward declarations of `struct module`, `struct key_entry`, and `struct asus_wmi`. It is included by the Asus WMI core and sibling model drivers, while public WMI device IDs come from `<linux/platform_data/x86/asus-wmi.h>`.

## Risks
Because the core mutates fields inside the model-provided `asus_wmi_driver`, callers must treat the descriptor as live driver state, not read-only metadata. Quirk defaults are security- and hardware-sensitive: a wrong display-toggle, fan, backlight, or hotplug quirk can suppress real events or write unsafe firmware state. Only one Asus WMI driver can be registered at a time in the core.

## Test Signals
Compile coverage should catch structure drift between model drivers and the core. Runtime signals include successful model-driver registration/unregistration, quirk detection being visible in `asus_wmi_add()`, key-filter behavior changing event reporting, and i8042 filters installing only for models that request them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/ayaneo-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/ayaneo-ec.c

## Purpose
`ayaneo-ec.c` is a DMI-gated platform driver for AYANEO handheld EC features. Depending on board quirks, it exposes fan monitoring/control through hwmon, battery charge-inhibit control through a power-supply extension, and AYANEO 3 magic-module controller power/status through sysfs.

## Important APIs, Types, And Functions
`struct ayaneo_ec_quirk` selects feature availability. `struct ayaneo_ec_platform_data` stores the platform device, quirks, battery hook, hwmon mutex, and restore flags for charge limit and PWM. The DMI table maps specific AYANEO board names to fan-only, fan-plus-charge, or AYANEO 3 feature sets.

Hwmon callbacks `ayaneo_ec_read()` and `ayaneo_ec_write()` use `ec_read()` and `ec_write()` against fixed EC registers for fan RPM, PWM value, and PWM mode. The power-supply extension callbacks map `POWER_SUPPLY_PROP_CHARGE_BEHAVIOUR` to EC values `0xaa` for auto and `0x55` for inhibit. `controller_power_*` and `controller_modules_show()` expose controller power and left/right module connection state.

## Control Flow
Module init creates a platform bundle. Probe checks DMI, allocates data, initializes the mutex, and conditionally registers an hwmon device and a battery hook. The driver-level `dev_groups` always points to the magic-module attribute group, but `aya_mm_is_visible()` hides those files unless the DMI quirk advertises magic modules.

Freeze records whether charge inhibit and manual PWM were active. If manual fan control was active, it switches the EC back to auto before hibernation to reduce overheat risk if resume fails. Restore reapplies charge inhibit when needed; PWM restoration is deliberately deferred until the next PWM write by userspace.

## State And Persistence
The EC is the source of truth for fan, charge, power, and module state. Kernel state records quirk selection and two restore booleans across hibernation. `restore_pwm` is protected by `hwmon_lock` because writes can race with PM state. Charge-inhibit state can be restored after hibernation, while manual PWM is not immediately restored for safety.

## Dependencies And Integration Points
The driver integrates with the ACPI EC accessors, DMI matching, hwmon, power-supply extension APIs, ACPI battery hooks, sysfs attribute groups, platform devices, and PM freeze/restore callbacks.

## Risks
All EC registers are hardcoded per AYANEO firmware convention; wrong DMI matching can expose writes on unsupported hardware. PWM conversion loses precision between 0-255 hwmon and 0-100 EC units. `ayaneo_psy_prop_is_writeable()` returns true for any queried property, relying on the property list and set callback to reject unsupported values. Manual fan mode is intentionally not restored immediately after hibernation, which may surprise users but avoids thermal risk.

## Test Signals
Validate DMI feature gating on each listed board, hwmon fan RPM and PWM mode/value reads, PWM write bounds and conversion, charge behavior get/set through the battery extension, hibernation freeze/restore behavior for charge inhibit and manual PWM, AYANEO 3 controller power toggling, module-state string mapping, and unload of the platform bundle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/ayaneo-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/barco-p50-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/barco-p50-gpio.c

## Purpose
`barco-p50-gpio.c` supports EC-connected identify LED and identify button GPIOs on Barco P50 boards. It translates a small EC mailbox over legacy I/O ports into a two-line GPIO chip, then instantiates standard `leds-gpio` and `gpio-keys-polled` consumers using software nodes.

## Important APIs, Types, And Functions
`struct p50_gpio` embeds the `gpio_chip`, a mutex for serialized EC mailbox access, the I/O port base, and child platform devices for LEDs and keys. Low-level helpers `p50_wait_ec()`, `p50_read_mbox_reg()`, and `p50_write_mbox_reg()` operate on ports `0x299` and `0x29a`. `p50_wait_mbox_idle()` and `p50_send_mbox_cmd()` implement the mailbox protocol with command, status, parameter, and data registers.

The GPIO callbacks are `p50_gpio_get_direction()`, `p50_gpio_get()`, and `p50_gpio_set()`. The LED line is output-only and the button line is input-only. Software nodes describe the LED as `identify` and the button as a polled `KEY_VENDOR` GPIO key.

## Control Flow
Module init DMI-matches Barco P50, registers the platform driver, and creates a simple platform device with the I/O resource. Probe reserves the I/O region, allocates state, initializes the GPIO chip, clears the mailbox, registers the gpiochip, registers software nodes, and creates `leds-gpio` and `gpio-keys-polled` child devices. Remove unregisters child devices and software nodes.

GPIO get/set operations lock the mutex, send a read or write mailbox command with the line-specific parameter, and read or write the mailbox data register. Mailbox status must report success or the operation returns `-EIO`.

## State And Persistence
The kernel stores only GPIO chip registration state and child device handles. LED/button values live in the EC. The mailbox is cleared at probe to remove stale commands. There is no suspend-specific state and no persistent configuration.

## Dependencies And Integration Points
The driver uses DMI, raw I/O port access, gpiochip, GPIO consumer software nodes, property APIs, `leds-gpio`, `gpio-keys-polled`, input event codes, and platform devices. It deliberately exports generic GPIO lines so standard LED and key drivers provide user-visible behavior.

## Risks
The mailbox uses polling loops and raw I/O, so timeouts or incorrect port ownership can block GPIO operations and return errors. `p50_gpio_get()` and `p50_gpio_set()` index `gpio_params[offset]`; callers are expected to pass valid GPIO offsets through gpiolib, but defensive bounds are limited to direction handling. Software-node and child-device cleanup ordering matters after partial probe failures.

## Test Signals
Test DMI gating, I/O region reservation failure, mailbox idle timeout handling, LED GPIO set/readback, button GPIO polling as `KEY_VENDOR`, software-node registration failure unwinding, child device registration failure unwinding, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/barco-p50-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/bitland-mifs-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/bitland-mifs-wmi.c

## Purpose
`bitland-mifs-wmi.c` is a WMI driver for Bitland notebooks implementing the MIFS/MiInterface protocol. It exposes system performance profile, fan and temperature monitoring, keyboard backlight brightness, GPU and keyboard RGB modes, fan boost, and selected hotkeys/events.

## Important APIs, Types, And Functions
The protocol uses packed `struct bitland_mifs_input`, `struct bitland_mifs_output`, and `struct bitland_mifs_event`. `bitland_mifs_wmi_call()` serializes WMI calls with a mutex and invokes either a procedure for SET operations without output or a method for GET operations with output.

`struct bitland_mifs_wmi_data` stores the WMI device, lock, keyboard LED, notifier block, input device, hwmon device, platform-profile device, and saved profile. The driver handles two WMI GUIDs: a control GUID for feature calls and an event GUID for notifications. A blocking notifier chain bridges event-device notifications to the control-device LED, hwmon, and platform-profile registrations.

Subsystem callbacks include `laptop_profile_get()/set()`, `laptop_hwmon_read()`, `laptop_kbd_led_set()/get()`, sysfs handlers for `gpu_mode`, `kb_mode`, and `fan_boost`, and `bitland_mifs_wmi_notify()` for event dispatch.

## Control Flow
Probe allocates state and initializes the WMI-call mutex. For the event GUID, it registers an input device using a sparse keymap for app/calculator/browser hotkeys. For the control GUID, it registers platform profile choices, an hwmon device, a keyboard backlight LED, and a notifier callback.

Profile set maps Linux platform profiles to firmware modes. Balanced-performance and performance first call `bitland_check_performance_capability()`, which requires system AC power and the circular-hole AC type rather than USB-C. Suspend saves the current profile and resume restores it.

Notifications validate event type, then update keyboard brightness, notify platform-profile changes, report sparse-keymap hotkeys, notify hwmon fan channels for CPU/GPU fan events, or log informational state changes.

## State And Persistence
The firmware stores all actual device state. The kernel caches only `saved_profile` for suspend/resume and registration objects. The blocking notifier chain is process-wide within the driver and allows the event WMI device instance to notify the control instance even though `no_singleton = true` permits both GUID-backed devices.

## Dependencies And Integration Points
The driver integrates with WMI device APIs, platform profile, power supply system-supplied checks, hwmon, LED class, input sparse keymaps, sysfs device groups, PM sleep ops, unaligned little-endian helpers, and a blocking notifier chain.

## Risks
The notifier chain assumes event and control devices coexist; events arriving before the control side registers will not update LED/hwmon/profile state. Performance profile writes are power-source gated and may fail when running on battery or USB-C. `bitland_mifs_wmi_call()` trusts output buffer sizing from `wmidev_invoke_method()` and copies the fixed output struct. Event hotkey reporting takes the WMI-call mutex even though it does not call WMI, which serializes against control calls but may be unnecessary.

## Test Signals
Test both WMI GUID instances, platform-profile get/set including AC-type rejection, suspend/resume profile restoration, hwmon CPU temp and three fan reads, keyboard LED get/set and hardware-change notification, sysfs `gpu_mode`, `kb_mode`, `fan_boost`, sparse key events for open-app/calculator/browser, fan event notifications to hwmon, and removal of notifier callbacks through devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/bitland-mifs-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/classmate-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/classmate-laptop.c

## Purpose
`classmate-laptop.c` supports Intel Classmate PC ACPI devices. It registers separate ACPI drivers for accelerometers, tablet-mode switch, backlight/rfkill control, and extra hotkeys, translating model-specific ACPI methods and notifications into standard Linux input, backlight, and rfkill interfaces.

## Important APIs, Types, And Functions
`struct cmpc_accel` stores accelerometer sensitivity, g-select, and open/closed state for v4 devices. `cmpc_add_acpi_notify_device()` and `cmpc_remove_acpi_notify_device()` are shared helpers for ACPI-notify-backed input devices.

There are two accelerometer implementations: v4 (`ACCE0001`) uses four-argument `ACMD` calls, signed 16-bit XYZ data, sensitivity and `g_select` sysfs attributes, and PM suspend/resume restart logic; pre-v4 (`ACCE0000`) uses two-argument `ACMD` calls, unsigned byte XYZ data, and a sensitivity attribute. Tablet mode (`TBLT0000`) uses `TCMD`. Backlight and WLAN rfkill (`IPML200`) use `GRDI`/`GWRI` commands for brightness selector `0xC0` and WLAN selector `0xC1`. Extra keys (`FNBT0000`) map low event nibbles to Linux key codes and use bit `0x10` as release state.

## Control Flow
Module init registers ACPI drivers in order: keys, IPML/backlight/rfkill, tablet, old accelerometer, and v4 accelerometer. On failure it unregisters previously registered drivers in reverse order. Exit unregisters all drivers.

Accelerometer add allocates state, writes default sensitivity and optionally g-select, creates sysfs attributes, then registers an input device. Opening the input device starts firmware reporting, notifications with event `0x81` read XYZ data and report ABS axes, and close stops reporting. V4 suspend stops the sensor only if it was open and resume reapplies settings and restarts it.

Tablet add registers an input switch device and initializes `SW_TABLET_MODE`; notification `0x81` refreshes state. IPML add registers a platform backlight and rfkill device against the same ACPI handle. Keys add registers an input device and reports key press/release from ACPI notify events.

## State And Persistence
Accelerometer sensitivity and g-select are kernel-side cached values mirrored into firmware when changed and when the v4 input device opens/resumes. V4 open state is tracked so suspend/resume only restarts active sensors. Backlight brightness and WLAN rfkill state live in ACPI firmware. Input devices and ACPI driver registrations are runtime-only.

## Dependencies And Integration Points
The driver depends on ACPI bus drivers and notifications, Linux input, backlight, rfkill, sysfs attributes, PM sleep ops, and standard module init/exit. It exposes multiple ACPI HIDs in one module through separate `struct acpi_driver` instances.

## Risks
Several ACPI buffer paths trust firmware object types and buffer lengths, especially accelerometer reads. Older accelerometer sensitivity has no explicit range check, while v4 validates sensitivity and g-select. `cmpc_ipml_add()` treats any non-NULL rfkill allocation as registerable, so error-pointer behavior relies on rfkill API conventions. Removal of accelerometer devices unregisters input devices but the allocated `cmpc_accel` state is not explicitly freed on normal remove in the visible code, which is a leak risk unless handled by surrounding kernel allocation semantics in this tree.

## Test Signals
Test registration/unregistration ordering, ACPI HID matching, accelerometer open/close and event `0x81` reports for old and v4 devices, v4 sysfs sensitivity/g-select validation and resume restart, tablet switch initial and notify state, backlight brightness get/set, WLAN rfkill query/block behavior, extra key press/release mapping including NL3 WLAN events, and init failure unwind at each ACPI driver registration step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/classmate-laptop.c -->
