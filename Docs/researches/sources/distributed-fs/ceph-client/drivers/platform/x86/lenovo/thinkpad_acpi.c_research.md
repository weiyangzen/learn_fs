# Research: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/thinkpad_acpi.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005142`: lines 1-9940, `Docs/researches/chunks/subset-b-005142_research.md`
- `subset-b-005143`: lines 9941-12275, `Docs/researches/chunks/subset-b-005143_research.md`

## Chunk Research

### subset-b-005142: lines 1-9940

# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/thinkpad_acpi.c lines 1-9940

## Scope

This chunk covers the first 9,940 lines of the ThinkPad ACPI extras driver. It includes the driver-wide constants and helper infrastructure, ACPI/procfs/platform-device glue, rfkill helpers, firmware-version and DMI quirk tables, and most major subdrivers through the beginning of the battery wear-control interface. The range ends inside the battery subdriver, after the `charge_behaviour_store()` implementation and immediately before the `DEVICE_ATTR_RW()` declarations and ACPI battery-hook registration that follow later in the file.

## Purpose

`thinkpad_acpi.c` is a platform driver for ThinkPad-specific firmware interfaces. The code in this chunk exposes vendor ACPI and embedded-controller features through Linux subsystems and legacy `/proc/acpi/ibm/*` files:

- HKEY hotkey/event handling, input-device reporting, ACPI netlink compatibility, tablet/radio switch state, adaptive keyboard mode, and TrackPoint double-tap toggling.
- Firmware-controlled Bluetooth, WWAN, and UWB radios through generic rfkill plus deprecated sysfs/proc controls.
- Legacy display-output switching, ThinkLight and keyboard backlight LED class devices, CMOS command passthrough, general ThinkPad LEDs, and beep commands.
- Thermal sensor access through hwmon, native brightness/backlight handling for older firmware, EC console audio/ALSA mixer support, fan speed/control/watchdog handling, and mute/micmute LEDs.
- Battery charge thresholds and charge behaviour support via Lenovo HKEY ACPI battery extension methods, though final attribute wiring is outside this chunk.

The file is intentionally compatibility-heavy: many branches exist for older IBM models, early Lenovo models, and newer Lenovo-specific ACPI methods that do not share one clean firmware contract.

## Important APIs, Types, and Functions

- `struct ibm_struct` is the per-subdriver descriptor. It supplies optional `read`, `write`, `init`, `exit`, `resume`, `suspend`, `shutdown`, and ACPI notify callbacks and carries flags for procfs and notify registration.
- `struct ibm_init_struct` ties a module parameter name, procfs mode, and `ibm_struct` together for the later module-init loop outside this chunk.
- `struct tp_acpi_drv_struct` describes an ACPI endpoint for a subdriver: HID table, ACPI handle, notify type, device, and notify callback.
- `struct thinkpad_id_data` stores DMI/firmware identity such as vendor, BIOS/EC model codes, releases, and model strings. `struct tpacpi_quirk` plus `TPACPI_Q_*` macros match that identity against quirk tables.
- `acpi_evalf()` is the central ACPI method wrapper. It accepts a compact format string: optional `q` for quiet, result type `d` or `v`, then integer arguments as `d`. Most hardware operations in the chunk go through this helper.
- `acpi_ec_read()` and `acpi_ec_write()` abstract direct EC access, optionally using legacy `ECRD`/`ECWR` ACPI methods on old systems.
- `setup_acpi_notify()` installs ACPI notify handlers for subdrivers and sets ACPI device class strings used by event delivery.
- `dispatch_proc_show()` and `dispatch_proc_write()` route legacy procfs files to the active `ibm_struct` read/write functions.
- `tpacpi_new_rfkill()`, `tpacpi_destroy_rfkill()`, `tpacpi_rfk_update_swstate()`, and `tpacpi_rfk_update_hwblock_state()` bridge ThinkPad radio methods to the kernel rfkill core.
- Hotkey state is centered on `hotkey_*` globals: `hotkey_all_mask`, `hotkey_reserved_mask`, `hotkey_driver_mask`, `hotkey_user_mask`, `hotkey_acpi_mask`, optional `hotkey_source_mask`, `hotkey_wakeup_reason`, and `hotkey_autosleep_ack`.
- `tpacpi_input_send_key()` maps HKEY event codes to sparse-keymap scancodes while preserving historical scancode ranges for original, adaptive, and extended hotkeys.
- `hotkey_notify()` drains HKEY events with `MHKP`, classifies them by high nibble, updates internal state, reports input switches/events, optionally emits ACPI netlink events, and calls `tpacpi_driver_event()` for cross-subdriver notifications.
- `tpacpi_brightness_*`, `volume_*`, and `fan_*` families implement stateful EC-backed controls for backlight, console audio, and fan control with mutexes and firmware-specific modes.
- `tpacpi_battery_get()`, `tpacpi_battery_set()`, `tpacpi_battery_set_validate()`, and `tpacpi_battery_probe()` implement the Lenovo battery extension method protocol for thresholds and charge behaviours.

## Control Flow

Module initialization, defined later in the file, calls into the subdriver `init` functions declared in this chunk. Each subdriver probes firmware capability by locating ACPI handles, checking DMI/BIOS/EC quirk tables, and evaluating feature-specific ACPI methods. Successful subdrivers register Linux-facing interfaces such as input, rfkill, led_classdev, backlight, ALSA, hwmon, sysfs attributes, and legacy procfs handlers.

ACPI helpers are initialized by locating core handles such as `ec`, `hkey`, `cmos`, `ecrd`, and `ecwr`. `acpi_evalf()` then provides the common execution path for ACPI calls and returns Linux-style success/error decisions to callers.

Hotkey handling starts by probing HKEY support and masks. `hotkey_init()` sets up the input device sparse keymap, reads initial radio/tablet/camera-shutter state, reserves brightness events when ACPI video owns backlight control, enables the firmware event interface with `MHKC`, programs the event mask via `MHKM`, and optionally starts an NVRAM polling kthread. Runtime ACPI notifications call `hotkey_notify()`, which repeatedly reads pending HKEY event codes from `MHKP`. Known events update internal state, input switches, rfkill state, thermal logs, or subdriver-specific state; unhandled events are logged and, unless suppressed, forwarded through ACPI netlink for compatibility.

When `CONFIG_THINKPAD_ACPI_HOTKEY_POLL` is enabled, `hotkey_kthread()` polls NVRAM for legacy events that firmware cannot deliver through HKEY. It compares old/new `struct tp_nvram_state` snapshots and synthesizes key events for volume, brightness, display, ThinkLight, zoom, and hibernate changes.

Radio subdrivers probe ACPI methods `GBDC`/`SBDC`, `GWAN`/`SWAN`, and `GUWB`/`SUWB`. They register rfkill switches and use WLSW as a shared hardware-block source. Bluetooth and WWAN shutdown paths ask firmware to save state to NVRAM through `\BLTH` or `\WGSV`.

Display, LED, beep, thermal, brightness, volume, and fan subdrivers follow the same broad pattern: detect an access mode, expose Linux interfaces, then translate sysfs/proc/ALSA operations into ACPI method calls or EC register reads/writes. The fan subdriver is the most complex in this chunk because it supports multiple read/write modes (`GFAN`, `FANG`, EC `0x2f`, non-standard EC addresses, `SFAN`, `FANW`, `FANS`), optional secondary fans, quirked RPM encodings, and a delayed watchdog that restores automatic fan operation.

The battery wear-control code probes HKEY battery extension methods such as `BCTG`, `BCSG`, `BDSG`, and `BICG`. It records per-battery threshold support and charge behaviour capability, then store/show helpers translate power_supply attributes into ACPI set/get calls. The sysfs attribute declarations and power_supply hook are just beyond this chunk.

## State and Persistence Behavior

The driver maintains runtime state in global/static variables rather than per-device instances. Important state includes `tp_features`, `thinkpad_id`, `tp_warned`, `tpacpi_lifecycle`, rfkill switch pointers, hotkey masks, LED state caches, brightness mode and maximum level, ALSA mixer state, fan access/control mode, fan desired/resume level, watchdog interval, mute LED state, and `battery_info`.

Some state is intentionally persisted through firmware or NVRAM:

- Bluetooth and WWAN shutdown/exit paths call firmware save-state commands so the radio state survives S4/S5.
- Brightness `ECNVRAM` mode checkpoints EC brightness into CMOS/NVRAM during suspend, shutdown, and exit.
- Volume `ECNVRAM` mode checkpoints console audio state into CMOS/NVRAM, and software mute can temporarily override the EC mute bit until exit/resume handling restores policy.
- Battery thresholds and charge behaviours are stored by firmware through ACPI extension methods, not in driver memory alone.

Other state is runtime-only and rebuilt after probe or resume. Hotkey masks are restored on resume, tablet/radio switch state is re-reported, adaptive keyboard mode is saved/restored across suspend, fan state is restored or made safe during resume, and mute LED class devices replay their cached state after resume.

## Dependencies and Integration Points

This chunk integrates with many kernel subsystems:

- ACPI core for device discovery, method evaluation, notify handlers, ACPI battery hooks later in the file, and ACPI video backlight arbitration.
- EC/NVRAM helpers for direct ThinkPad embedded-controller registers and CMOS/NVRAM persistence.
- input and sparse-keymap for hotkeys, radio switch, tablet mode, and camera shutter switch reporting.
- rfkill for Bluetooth, WWAN, and UWB radio controls.
- platform device/driver and sysfs attribute groups for `thinkpad_acpi`, hwmon, and driver attributes.
- procfs/seq_file for the legacy `/proc/acpi/ibm` ABI.
- hwmon for thermal sensors and fan tachometer/PWM-style controls.
- LED class for keyboard backlight, ThinkLight, general ThinkPad LEDs, and platform mute/micmute LEDs.
- backlight core for `thinkpad_screen`.
- ALSA control core for the optional ThinkPad EC console audio mixer.
- power_supply core for battery charge threshold and charge behaviour attributes, with the actual hook registration after this range.
- DMI and PCI tables for quirks, including the AMD ThinkPad/Intel Bluetooth firmware bug detection.

The code also depends on compile-time configuration gates such as `CONFIG_THINKPAD_ACPI_HOTKEY_POLL`, `CONFIG_THINKPAD_ACPI_DEBUG`, `CONFIG_THINKPAD_ACPI_DEBUGFACILITIES`, `CONFIG_THINKPAD_ACPI_VIDEO`, `CONFIG_THINKPAD_ACPI_ALSA_SUPPORT`, and `CONFIG_THINKPAD_ACPI_UNSAFE_LEDS`.

## Risks and Edge Cases

- `acpi_evalf()` is a small custom ABI. Wrong format strings or incorrect quiet/result-type usage can silently turn firmware failures into missing features or noisy probe failures.
- The driver has many global state variables and cross-subdriver calls. Hotkey events call rfkill, brightness, thermal, palm sensor, and later platform-profile handlers, so changing event classification can regress unrelated features.
- Hotkey masks combine firmware-delivered events and NVRAM-polled events. Incorrect mask synchronization can either drop driver-required events or re-enable firmware events that the driver intentionally reserved.
- Sparse-keymap scancode compatibility is part of userspace ABI. The original, adaptive, and extended HKEY ranges must keep their historical scancode translations.
- Deprecated procfs and sysfs interfaces remain functional. They parse comma-separated command strings and often expose privileged or hardware-sensitive controls; permissive changes can revive unsafe behaviour.
- Radio control has both software and hardware blocking. WLSW state must be synchronized before input rfkill events to avoid races with the rfkill core.
- Video switching is explicitly dangerous on old systems; the code requires `CAP_SYS_ADMIN` and warns that even reads can crash X.org.
- LED control restricts most firmware LEDs unless `CONFIG_THINKPAD_ACPI_UNSAFE_LEDS` is enabled. Removing that guard can let userspace override safety/status LEDs.
- Thermal and fan EC addresses vary by model. Non-standard EC address quirks, decimal RPM encoding, ticks-per-revolution conversion, secondary-fan selection, and uninitialized HFSP handling are model-sensitive.
- Fan control is safety-critical. Manual level, full-speed/disengaged modes, watchdog rescheduling, and resume restoration must preserve automatic cooling when the driver exits or errors.
- Brightness and volume EC/NVRAM modes are limited to specific old IBM/early Lenovo firmware assumptions. Using EC HBRV or audio EC registers on unsupported models can corrupt unrelated EC state.
- Battery setters validate thresholds against cached opposite thresholds. If firmware changes thresholds externally, stale `battery_info` can reject valid writes or accept values based on outdated state until the next read/probe updates expectations.
- Battery charge behaviour uses `min(ret, ...)` while sequencing multiple set/validate operations. Because `ret` starts at zero, failures can be preserved, but reviewers should be careful when changing ordering or return folding.
- The requested range ends before battery attribute declarations and hook registration, so this chunk alone does not show how the battery helpers become visible through `power_supply`.

## Test Signals

Useful validation signals for this chunk include:

- Module load/probe logs with `debug=` bitmasks for init, HKEY, rfkill, fan, brightness, and mixer paths; look for missing ACPI handles, outdated firmware warnings, unsupported feature messages, and quirk notices.
- `/sys/devices/platform/thinkpad_acpi/` hotkey attributes: masks, radio switch, tablet mode, adaptive keyboard mode, and doubletap toggling should match firmware capabilities.
- `evtest` or libinput monitoring of ThinkPad hotkeys, tablet mode, radio switch, camera shutter, and TrackPoint doubletap, including suppression of known duplicate or reserved events.
- `rfkill list` plus deprecated `bluetooth_enable`/`wwan_enable` reads on machines with radios, verifying WLSW hardware-block behaviour and resume/shutdown state preservation.
- `sensors`/hwmon reads for `temp*_input`, `fan*_input`, `pwm1`, and `pwm1_enable`, with model-specific checks for second fan and non-standard EC quirks.
- Fan safety tests with `fan_control=1`: manual level, auto mode, full-speed/disengaged mapping, watchdog timeout, suspend/resume restoration, and module unload returning control to firmware.
- Backlight tests on old IBM/early Lenovo systems only: `thinkpad_screen` registration, hotkey updates, NVRAM checkpoint on suspend/shutdown, and correct non-registration when ACPI video owns backlight.
- ALSA mixer tests for `ThinkPad Console Audio Control`, including mute-only Lenovo systems, read-only monitor mode, `volume_control=1`, and software mute startup/exit behaviour.
- Battery threshold tests on supported Lenovo firmware: `charge_control_start_threshold`, `charge_control_end_threshold`, and `charge_behaviour` should reject invalid ranges, reflect firmware state after set/validate, and handle BAT0/BAT1 addressing correctly.

### subset-b-005143: lines 9941-12275

# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/thinkpad_acpi.c lines 9941-12275

## Scope

This chunk covers the final third of `thinkpad_acpi.c`. It starts at the battery sysfs attribute group and ACPI battery hook registration, then defines several late ThinkPad-specific subdrivers: Lenovo PrivacyGuard/LCD shadow, proximity sensors, DYTC platform profiles, keyboard language selection, Dynamic Power Reduction Control antenna reporting, auxiliary MAC address pass-through, and Lenovo Hardware Damage Detection. It then collects sysfs attribute groups, defines platform drivers, routes HKEY events to subdrivers, implements generic `ibm_struct` initialization and teardown, probes DMI/ACPI identity data, declares module parameters, and performs module init/exit.

The chunk is not standalone. Many helpers, globals, event constants, ACPI handles, `struct ibm_struct`, `struct ibm_init_struct`, the procfs dispatch layer, power-management hooks, and older subdrivers are defined earlier in the same file. This range is the integration and lifecycle end of the driver.

## Purpose

The code turns previously defined ThinkPad ACPI capabilities into Linux-visible devices and attributes, and it wires those features into the module lifecycle:

- Attach ThinkPad battery charge-control attributes to ACPI battery `power_supply` devices.
- Register a DRM privacy-screen provider for Lenovo PrivacyGuard and expose legacy `/proc/acpi/ibm/lcdshadow` control.
- Expose palm and lap sensor state via platform-device sysfs attributes, with HKEY event refresh and sysfs notifications.
- Map Lenovo DYTC firmware thermal/performance modes to the Linux platform profile API.
- Expose and set keyboard language firmware state for layout-dependent key emulation.
- Report WWAN antenna type from the DPRC ACPI method.
- Publish the firmware-provided MAC Address Pass-through value through a read-only string attribute.
- Report USB Type-C hardware damage detection capability and status from Lenovo HWDD firmware.
- Build the final platform, hwmon, sysfs, procfs, input, workqueue, DMI, and module-parameter initialization paths.

## Important APIs, Types, and Data

Battery integration uses `struct acpi_battery_hook battery_hook`, `battery_hook_register()`, `battery_hook_unregister()`, `tpacpi_battery_add()`, and `tpacpi_battery_remove()`. `tpacpi_battery_attrs` adds `charge_control_start_threshold`, `charge_control_end_threshold`, legacy `charge_start_threshold`, legacy `charge_stop_threshold`, and `charge_behaviour` to each probed battery that passes `tpacpi_battery_probe()`. The `battery_quirk_table` sets `tp_features.battery_force_primary` for models whose ACPI BAT numbering breaks individual battery addressing.

PrivacyGuard is represented by `struct drm_privacy_screen *lcdshadow_dev` plus ACPI method handles `GSSS` and `SSSS`. `lcdshadow_ops` registers `lcdshadow_set_sw_state()` and `lcdshadow_get_hw_state()` with the DRM privacy screen framework. The same device is also controlled by `lcdshadow_read()` and `lcdshadow_write()` through the legacy IBM procfs mechanism.

Sensor and profile support centers on DYTC. `dytc_command()` evaluates the HKEY `DYTC` ACPI method. The proximity layer uses `DYTC_CMD_GET` and bit `DYTC_GET_LAPMODE_BIT` for lap mode, plus the `GPSS` ACPI method for the palm sensor. The platform profile layer uses DYTC capability bits `DYTC_FC_MMC`, `DYTC_FC_PSC`, and `DYTC_FC_AMT`, function IDs `DYTC_FUNCTION_MMC`, `DYTC_FUNCTION_PSC`, `DYTC_FUNCTION_AMT`, mode constants for MMC/PSC/AMT, and `DYTC_SET_COMMAND()` command packing. It exposes `dytc_profile_ops` through `platform_profile_register()`.

Keyboard language support uses static `keyboard_lang_data[]` string-to-firmware-code mappings, ACPI methods `GSKL` and `SSKL`, and the `keyboard_lang` sysfs attribute. DPRC support uses `dprc_command()`, command `DPRC_GET_WWAN_ANTENNA_TYPE`, and firmware bits for type A/type B WWAN antenna reporting. Auxiliary MAC support evaluates the absolute ACPI object `\\MACA`, validates marker characters in the returned string, and stores either a 12-character MAC-like value, `disabled`, or `unavailable` in `auxmac`.

HWDD support uses the `HWDD` ACPI method with `HWDD_GET_CAP` and `HWDD_GET_DMG_USBC`. Status fields are decoded with `FIELD_GET()` masks for port, lid, base, panel, and position information. It exposes `hwdd_status` as a boolean damage-present indicator and `hwdd_detail` as decoded text.

The final infrastructure uses `struct platform_driver tpacpi_pdriver`, `struct platform_driver tpacpi_hwmon_pdriver`, `tpacpi_groups`, `tpacpi_hwmon_groups`, `ibms_init[]`, `ibm_init()`, `ibm_exit()`, `tpacpi_pdriver_probe()`, `thinkpad_acpi_module_init()`, and `thinkpad_acpi_module_exit()`. DMI parsing is handled by `tpacpi_parse_fw_id()`, `find_new_ec_fwstr()`, `get_thinkpad_model_data()`, and `probe_for_thinkpad()`.

## Control Flow

Battery setup is late-bound to ACPI battery devices. `tpacpi_battery_init()` clears cached battery info, checks battery quirks, then registers `battery_hook`. When the ACPI battery core reports a battery, `tpacpi_battery_add()` derives its ThinkPad battery ID from the power-supply name, probes ThinkPad charge-control support, and adds the battery attribute groups. Removal detaches the groups.

PrivacyGuard initialization first locates `GSSS` and `SSSS`. If either handle is absent, the subdriver is silently unavailable. If `GSSS` evaluates successfully and advertises support through bit `0x10000`, the code registers a DRM privacy-screen object. State changes flow through either the DRM privacy-screen `set_sw_state` callback or the legacy procfs write handler. Both call firmware through `SSSS`; the HKEY privacy-toggle event refreshes hardware state through `GSSS` and notifies the DRM privacy-screen chain if the state changed.

Proximity-sensor initialization probes both palm and lap paths. It returns unavailable only when both paths report `-ENODEV`, but propagates other firmware errors. Attribute visibility hides `dytc_lapmode` unless a lap sensor exists and DYTC version is at least 5, and hides `palmsensor` unless the palm sensor exists. HKEY thermal-control completion events call `lapsensor_refresh()`, which re-reads state and issues `sysfs_notify()` when the lap bit changes.

DYTC profile initialization queries DYTC, extracts `dytc_version`, rejects versions below 5, queries function capabilities, optionally applies the `profile_force` module parameter, selects MMC or PSC behavior, checks whether `DYTC_CMD_MMC_GET` works for DYTC v6+, adjusts PSC mode constants for DYTC v9+, registers the platform-profile device, refreshes the initial profile, and for PSC applies a balanced-mode workaround. Profile `get` returns the cached `dytc_current_profile`; profile `set` converts the requested Linux profile to a firmware mode, serializes firmware access with `dytc_mutex`, then sends either MMC or PSC commands. MMC balanced mode uses `DYTC_CMD_RESET`; other MMC profile changes use a CQL-aware wrapper that temporarily disables lap mode and restores it. PSC profile changes optionally toggle AMT for balanced mode.

`dytc_profile_refresh()` is the event-side sync path. It reads MMC or PSC firmware state, converts function/mode pairs back to Linux platform profiles, updates `dytc_current_profile`, and calls `platform_profile_notify()` when userspace-visible state changed. `dytc_ignore_event` suppresses one firmware-generated thermal event while the driver temporarily toggles CQL.

Keyboard language control is simple sysfs command handling. The show path reads `GSKL`, matches the returned code against `keyboard_lang_data[]`, and prints all supported language tokens with the active token bracketed. The store path accepts a known language string, sets bit 24 in the firmware language code, calls `SSKL`, discloses the user task, and notifies the attribute.

DPRC and HWDD are probe-then-display subdrivers. DPRC initialization reads the WWAN antenna command once, stores type A or type B, and later `wwan_antenna_type_show()` returns the cached value. HWDD initialization reads capabilities, records whether HWDD and USB-C damage detection are supported, and show paths re-query `HWDD_GET_DMG_USBC` so status/detail reflect current firmware state.

The main module flow starts in `thinkpad_acpi_module_init()`: gather DMI identity, reject non-ThinkPad/non-Lenovo/unsupported ACPI systems, print a banner, check outdated firmware, locate EC read/write methods, create the workqueue and proc directory, load DMI quirk data, register the main platform device, probe the main platform driver, then create the hwmon platform bundle. The main platform probe allocates the input device, detects brightness capabilities, iterates `ibms_init[]` to initialize every subdriver, applies module-load procfs command parameters, installs a devm cleanup action for subdrivers, and finally registers the input device.

Teardown reverses the major resources. `tpacpi_subdrivers_release()` walks `tpacpi_all_drivers` in reverse and calls `ibm_exit()` for each initialized subdriver. `ibm_exit()` removes ACPI notify handlers, removes proc entries, and calls subdriver exit hooks. `thinkpad_acpi_module_exit()` unregisters hwmon and platform devices/drivers, removes procfs, destroys the workqueue, and frees DMI strings.

## State and Persistence

Most state in this chunk is module-global because `thinkpad_acpi.c` models ThinkPad firmware as one platform device. Persistent runtime state includes:

- Battery quirk and probe state in `tp_features.battery_force_primary` and `battery_info`.
- PrivacyGuard handles and current DRM privacy-screen state in `lcdshadow_dev`, `lcdshadow_get_handle`, and `lcdshadow_set_handle`.
- Proximity state in `has_palmsensor`, `has_lapsensor`, `palm_state`, `lap_state`, and `dytc_version`.
- DYTC profile state in `dytc_current_profile`, `dytc_capabilities`, `dytc_mmc_get_available`, `dytc_amt_active`, PSC mode mapping globals, `dytc_ignore_event`, and `profile_force`.
- Keyboard-language support flag `tp_features.kbd_lang`.
- DPRC/HWDD support and cached values in `has_antennatype`, `wwan_antennatype`, `hwdd_support_available`, and `ucdd_supported`.
- Auxiliary MAC state in the static `auxmac` buffer.
- Platform lifecycle state in `tpacpi_lifecycle`, `tp_features.platform_drv_registered`, `tpacpi_pdev`, `tpacpi_sensors_pdev`, `tpacpi_wq`, `proc_dir`, `tpacpi_inputdev`, `tpacpi_hwmon`, and allocated strings in `thinkpad_id`.

Firmware state can outlive the driver. DYTC profile changes, AMT toggles, PrivacyGuard state, keyboard language selection, and battery charge thresholds are ACPI firmware/device settings, not just Linux caches. The driver caches enough state for sysfs presentation and notification, but many show paths re-read firmware because hardware state can change through hotkeys, BIOS, or platform control.

## Dependencies and Integration Points

The chunk integrates with several kernel subsystems:

- ACPI method evaluation through `acpi_get_handle()`, `acpi_evalf()`, `acpi_evaluate_object()`, DMI scanning, and ThinkPad-specific HKEY event delivery.
- The power-supply ACPI battery hook API for adding battery charge-control sysfs attributes.
- The DRM privacy-screen framework for PrivacyGuard state, locking, and notifier delivery.
- The platform profile API for low-power, balanced, and performance profile selection.
- Sysfs attribute groups on the main platform device, driver attributes, and the hwmon device.
- HWMON registration for thermal and fan groups created earlier in the file.
- The input subsystem for ThinkPad extra buttons and switch events such as camera shutter state.
- Procfs compatibility under `/proc/acpi/ibm`, including module parameters that simulate procfs commands at module load.
- Platform device/driver registration for the main `thinkpad_acpi` device and the separate hwmon bundle.

The HKEY event dispatcher is a major integration point. It forwards brightness, volume, keyboard-backlight, adaptive-keyboard, thermal/DYTC, PrivacyGuard, AMT, camera shutter, TrackPoint double-tap, and platform-profile toggle events to the relevant subdriver or subsystem. Some events return `false` so the hotkey path can still report key presses when user masks request them; others return `true` after the driver consumes the platform event.

## Risks

- ACPI method contracts are firmware-specific. Wrong assumptions about return bits from `DYTC`, `GPSS`, `GSKL`, `DPRC`, `HWDD`, or `\\MACA` can hide valid features, expose invalid sysfs state, or send unsupported commands.
- DYTC profile handling has subtle state coupling with lap mode. The CQL wrapper increments `dytc_ignore_event`, disables CQL, runs the command, and re-enables CQL; failure in either disable or re-enable paths can leave lap-mode/profile state inconsistent.
- `convert_profile_to_dytc()` returns success even if neither MMC nor PSC capability filled `*perfmode`; current init normally prevents that, but future capability combinations or forced profiles could expose an uninitialized mode value.
- `dytc_profile_set()` ignores the return value from `dytc_control_amt()` in the PSC path, so an AMT toggle failure does not fail the platform-profile set operation.
- PrivacyGuard write notifies the DRM chain after calling `lcdshadow_set_sw_state()` regardless of whether the set failed, which can produce notifications without a real hardware change.
- `lcdshadow_exit()` calls `drm_privacy_screen_unregister(lcdshadow_dev)` without a local null/error guard; current `ibm_init()` marks the subdriver initialized only after successful init, so this relies on lifecycle ordering.
- HWDD capability naming is easy to misread: `tpacpi_hwdd_init()` treats `!(output & HWDD_NOT_SUPPORTED)` as unavailable, so the firmware bit appears to mean support is available despite its name. This is worth preserving carefully in changes.
- `auxmac_init()` frees `obj` rather than `buffer.pointer`; that is equivalent here because `obj` aliases `buffer.pointer`, but changes to the buffer handling should keep ownership clear.
- Subdriver initialization is tolerant of `-ENODEV`, but any other error aborts the whole driver probe. Firmware bugs in late optional features can therefore prevent unrelated ThinkPad ACPI functionality from loading.
- Module exit cleanup is broad and global. Partial-init errors depend on `thinkpad_acpi_module_exit()` and devm actions to handle null/unregistered objects correctly.

## Test and Validation Signals

Useful validation signals for this chunk are mostly runtime and hardware/firmware-facing:

- Module load on supported and unsupported machines should show correct DMI banner behavior, reject non-ThinkPad systems unless `force_load` applies, create `/proc/acpi/ibm`, register the main platform device, register input, and register hwmon.
- Battery charge-control attributes should appear only on batteries that pass ThinkPad probing, and should be removed when ACPI battery devices go away.
- PrivacyGuard systems should create a DRM privacy-screen device, reflect hotkey toggles through notifier calls, preserve the selected state across resume, and reject invalid procfs values.
- `dytc_lapmode` and `palmsensor` should appear only when firmware support is present; HKEY thermal-completion events should update lap state and notify sysfs.
- Platform profile choices should expose low-power, balanced, and performance; setting each profile should update firmware and `platform_profile_notify()` should fire when firmware/hotkey changes alter the current profile.
- DYTC edge testing should cover MMC with and without `DYTC_CMD_MMC_GET`, PSC on DYTC v5-v8 and v9+, AMT hotkey toggles, `profile_force=-1/1/2`, and CQL/lap-mode preservation.
- Keyboard language sysfs should list all known tokens, bracket the current one, reject unknown strings, and call firmware with bit 24 set for accepted stores.
- DPRC should expose `wwan_antenna_type` only when type A or B is reported, and `METHOD_ERR` returns should leave the attribute hidden.
- Auxmac should report hidden/absent before successful probe, `disabled` for `XXXXXXXXXXXX`, `unavailable` for malformed buffers, and the firmware string for valid pass-through data.
- HWDD should hide attributes when unsupported, return `0` or `1` for current USB-C damage status, and decode detail text for each reported port/location combination.
- Failure-path tests should inject missing ACPI handles, `METHOD_ERR`, invalid object types, allocation failures, platform registration failures, and subdriver init errors to verify cleanup and that optional `-ENODEV` features do not abort module load.
