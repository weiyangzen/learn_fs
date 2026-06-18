## sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-wmi.c

Purpose: Eee PC WMI hotkey driver built on the shared `asus-wmi` framework. It covers WMI event GUID `ABBC0F72-8EA1-11D1-00A0-C90629100000` and avoids binding when the legacy ASUS010 ATKD ACPI device is also active.

Important APIs/functions: `eeepc_wmi_keymap` maps ASUS WMI brightness, volume, WLAN, touchpad, camera, display, and special keys. DMI quirks configure wireless hotplug and ET2012 backlight behavior through `struct quirk_entry`. `et2012_quirks()` inspects OEM strings to choose panel-brightness quirks. `eeepc_wmi_key_filter()` converts T101MT Home press/release scancodes into non-autoreleased key transitions and suppresses hold events. `eeepc_wmi_probe()` rejects systems with legacy ATKD present. `eeepc_wmi_quirks()` initializes the asus-wmi driver quirk pointer and panel power defaults.

Control flow: module init calls `asus_wmi_register_driver()` with a populated `struct asus_wmi_driver`; exit unregisters it. The asus-wmi core owns platform device creation, input registration, WMI notification dispatch, and most hardware operations, while this file supplies keymap/filter/probe/quirk callbacks.

State and persistence: only static quirk pointers and module parameter `hotplug_wireless` are stored here. Firmware state is managed by asus-wmi.

Dependencies and integration: `asus-wmi.h`, DMI/OEM string matching, ACPI legacy-device detection, backlight constants, input sparse-keymap through the asus-wmi core.

Risks: quirk selection mutates a global `quirks` pointer and then writes fields before registration; shared static quirk objects must not be unexpectedly reused across devices. Legacy ATKD detection is important to avoid duplicate hotkey handling. Test signals include WMI-only systems, ATKD conflict path, ET2012 OEM string variants, Home press/hold/release behavior, `hotplug_wireless` parameter, and keymap coverage through asus-wmi events.
