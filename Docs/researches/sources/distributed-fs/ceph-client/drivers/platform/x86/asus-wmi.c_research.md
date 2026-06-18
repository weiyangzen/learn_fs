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
