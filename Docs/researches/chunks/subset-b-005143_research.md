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
