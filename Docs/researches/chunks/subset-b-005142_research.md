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
