# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-laptop.c

Purpose: Dell laptop extras driver over Dell SMBIOS. It provides rfkill, vendor display backlight, touchpad LED quirks, keyboard backlight LED/sysfs controls, audio mute LEDs, and ACPI battery charge-mode/threshold extensions.

Important APIs/types/functions: `dell_send_request_for_tokenid()` token helper; rfkill setup/update and i8042/dell-rbtn event paths; `dell_ops` backlight; keyboard state structures and `kbd_get_info`, `kbd_get_state`, `kbd_set_state_safe`, `kbd_led_*`; mute LED setters; `dell_battery_*` and `acpi_battery_hook`.

Control flow/state/persistence: `late_initcall(dell_init)` checks Dell laptop DMI, registers platform device, sets up rfkill, quirk LEDs, keyboard LED, battery hook, debugfs, notifier, mute LEDs, and optional vendor backlight. State includes registration flags, rfkill pointers, keyboard capability/cache variables, and battery mode bitmap. Actual settings live in firmware/SMBIOS tokens.

Dependencies/integration: `dell-smbios`, optional dynamic `dell-rbtn` notifiers, i8042 fallback, ACPI battery, power_supply, backlight, LED class, debugfs, and Dell WMI privacy helper.

Risks/test signals: Many model quirks and multiple keyboard backlight mechanisms. Test rfkill on whitelisted systems, `dell-rbtn` and i8042 events, backlight token reads/writes, keyboard brightness/timeouts/triggers/ALS, battery charge type and thresholds, mute LEDs, and all init-failure unwind paths.
