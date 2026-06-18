<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c

## Purpose
This Lenovo GameZone WMI driver maps Lenovo Legion thermal modes to the Linux `platform_profile` interface. It also exposes the current GameZone thermal mode to other Lenovo WMI drivers through the helper notifier chain.

## Important APIs, Types, And Functions
`struct lwmi_gz_priv` stores current thermal mode, event and mode notifier blocks, a spinlock, WMI device, extreme-mode support, and registered platform-profile device. WMI method IDs `43`, `44`, and `45` query support, set SmartFan mode, and get SmartFan mode. `lwmi_gz_profile_get()` and `lwmi_gz_profile_set()` implement `platform_profile_ops`; `lwmi_gz_platform_profile_probe()` populates supported profile choices. `lwmi_gz_event_call()` consumes thermal mode events from `wmi-events.c`; `lwmi_gz_mode_call()` answers `LWMI_GZ_GET_THERMAL_MODE` requests from `wmi-helpers.c`.

## Control Flow
Probe registers a platform-profile provider, initializes the spinlock, reads current thermal mode, subscribes to WMI thermal events, and registers a thermal-mode query notifier. Profile get reads firmware and updates cached mode. Profile set converts Linux profile options to Lenovo thermal modes, calls WMI method `SMARTFAN_SET`, and updates cached mode. Event notifications update cached mode and call `platform_profile_notify()`.

## State And Persistence
The cached `current_mode` is protected by `gz_mode_lock`; firmware remains authoritative and is read during profile get. No persistent state is stored by the driver beyond WMI-set thermal mode in firmware/EC.

## Dependencies And Integration Points
The driver depends on Lenovo GameZone WMI GUID `887B54E3-DDDC-4B2C-8B88-68A26A8835D0`, `platform_profile`, DMI quirks, `wmi-events`, and `wmi-helpers`. `wmi-other.c` queries current mode before exposing or setting custom CPU power attributes.

## Risks And Edge Cases
Extreme mode is gated by interface version and DMI firmware-bug quirks for Legion Go models that report support but lack correct BIOS entries. The profile set path does not explicitly reject unsupported `MAX_POWER` when the bit was not advertised, relying on platform-profile choices to prevent selection. Notifier pointer handling in `lwmi_gz_mode_call()` is pointer-to-pointer and must match `lwmi_tm_notifier_call()`.

## Test Signals
Tests should verify supported profile bitmaps for WMI support versions below and above 6, DMI quirk suppression of extreme mode, get/set WMI method behavior, event-driven profile notifications, and `wmi-other` custom-mode gating through `lwmi_tm_notifier_call()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c -->
