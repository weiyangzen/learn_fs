# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-wmi.c

Purpose: HP laptop WMI extras driver. It handles WMI hotkeys and switches, rfkill, legacy sensor sysfs files, camera shutter events, platform profiles for generic/OMEN/Victus systems, fan hwmon controls, and AC power-source profile restoration.

Important APIs/types/functions: `hp_wmi_perform_query()` is the central BIOS WMI method wrapper. Input handling uses `hp_wmi_keymap`, `hp_wmi_notify()`, and `hp_wmi_input_setup()`. Wireless control uses legacy rfkill and rfkill2 paths. Thermal/profile code includes OMEN/Victus DMI tables, `thermal_profile_setup()`, platform profile ops, and AC notifier callbacks. Hwmon support uses `struct hp_wmi_hwmon_priv`, `hp_wmi_apply_fan_settings()`, and hwmon read/write callbacks.

Control flow: module init checks event and BIOS GUIDs, detects zero-input-size firmware behavior, sets up input notify handling, registers a platform device/driver for BIOS features, detects board-specific thermal parameters, initializes rfkill, hwmon, and platform profile support, and optionally registers AC notifiers. WMI notifications decode event buffers into dock/tablet switches, sparse-keymap events, rfkill refreshes, platform-profile cycling, or camera shutter switch events. Exit unregisters notifiers, input devices, rfkill, hwmon keepalive, platform objects, and profile notifiers.

State and persistence: runtime globals track input devices, platform device, rfkill objects, platform profile state, zero-size-query quirk, board-specific profile parameters, and fan keepalive state. Some settings persist in firmware or EC, while `active_platform_profile` caches user intent because firmware may reject or revert performance mode on battery.

Dependencies and integration: ACPI WMI/EC, DMI, input sparse keymap, rfkill, power_supply, platform_profile, hwmon, workqueues, and sysfs device attributes.

Risks: the file mixes many hardware generations and DMI quirks, so regressions can be board-specific. WMI output parsing assumes HP buffer formats. Fan manual mode requires periodic keepalive. Test signals include WMI GUID combinations, hotkey events, rfkill2 device parsing, suspend/resume state refresh, platform-profile get/set on generic and OMEN/Victus boards, AC notifier behavior, and hwmon fan/pwm reads/writes.
