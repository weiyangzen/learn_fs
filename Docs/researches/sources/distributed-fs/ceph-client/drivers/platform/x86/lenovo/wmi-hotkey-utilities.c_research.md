<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c

## Purpose
This Lenovo Super Hotkey Utility WMI extras driver exposes firmware-controlled audio mute and microphone mute LEDs as Linux LED class devices.

## Important APIs, Types, And Functions
The driver targets WMI GUID `CE6C0974-0407-4F50-88BA-4FC3B6559AD8`. `struct wmi_led_args` is the SetFeature payload. `struct lenovo_super_hotkey_wmi_private` stores two `led_classdev` objects and the WMI device. `lsh_wmi_mute_led_set()` maps LED brightness to firmware feature IDs for mic or audio mute. `lenovo_super_hotkey_wmi_led_init()` queries support version, validates expected version constants, initializes LED classdev names/triggers, and registers them.

## Control Flow
Probe allocates private data, stores the WMI device, and calls setup for mic then audio LEDs. Each setup call invokes `WMI_LUD_GET_SUPPORT`; version `0` means unsupported, exact version matches enable registration. Brightness changes use `WMI_LUD_SET_FEATURE` with one of four on/off feature IDs.

## State And Persistence
The driver does not cache brightness. LED state is held in firmware and controlled through WMI calls. LED class devices are devm-registered and cleaned up with device removal.

## Dependencies And Integration Points
It depends on WMI, ACPI buffer calls, LED class devices, and default audio triggers `audio-micmute` and `audio-mute`. Userspace and ALSA trigger logic can drive the LEDs through the standard LED subsystem.

## Risks And Edge Cases
Unsupported or unexpected firmware LED versions are silently skipped after warnings. SetFeature failures return `-EIO` to LED core. The driver accepts any non-zero brightness as `LED_ON` through wrapper callbacks but registers max brightness as `LED_ON`.

## Test Signals
Validation should include support-version queries for both LED types, LED class device names `platform::micmute` and `platform::mute`, trigger activation, WMI SetFeature payload inspection, suspend/resume LED restoration, and behavior on unsupported version returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c -->
