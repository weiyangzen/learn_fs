## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.c

Purpose: handles Dell hardware privacy status for microphone, camera shutter, and ePrivacy screen capability/status reporting. It registers a WMI driver through `dell-wmi-base`, exposes sysfs status, reports input events, and provides a micmute LED device used as an EC acknowledgement trigger.

Important APIs, types, and functions: `struct privacy_wmi_data` stores input device, WMI device, list node, LED classdev, supported feature mask, and last status. `dell_privacy_has_mic_mute()` and `dell_privacy_process_event()` are exported for other Dell modules. `get_current_status()` reads an 8-byte WMI block containing supported devices and current state. `dell_privacy_wmi_probe()` builds a sparse keymap for type `0x0012` privacy events, conditionally registers camera switch support, reports initial camera-cover state, and registers `dell-privacy::micmute` if audio privacy is present. `dell_privacy_micmute_led_set()` evaluates EC method `ECAK`.

Control flow: `dell-wmi-base` calls `dell_privacy_register_driver()` during module init and delegates type `0x0012` events to `dell_privacy_process_event()`. Audio events set `last_status` and emit `KEY_MICMUTE`; camera events emit `SW_CAMERA_LENS_COVER` according to the status bit. Sysfs attributes render supported and current state per privacy type.

State and persistence: a mutex-protected global WMI list stores active privacy devices, but helpers use the first entry. `last_status` is updated from initial WMI block and event payloads. The LED operation does not set brightness itself; it acknowledges firmware/EC sequencing.

Dependencies and integration: WMI, ACPI EC, input sparse-keymap, switch events, LED trigger `audio-micmute`, sysfs device groups, and `dell-wmi-base` event parsing.

Risks: only the first privacy device is used. EC method `ECAK` may be missing. Incorrect status-bit interpretation would invert camera cover or mic state. Test signals include initial sysfs state, camera-cover switch registration only when supported, micmute LED trigger behavior, WMI block validation, unknown privacy event logging, and integration with audio codec micmute notifications.
