# sources/distributed-fs/ceph-client/drivers/hid/hid-corsair.c

Purpose: supports Corsair gaming keyboards and mice, especially K90 macro/backlight controls, K70/K90 special-key mapping, and descriptor fixups for GLAIVE RGB and Scimitar Pro RGB mice.

Important APIs/types/functions: `struct corsair_drvdata` stores quirk flags plus K90 macro/backlight state. `struct k90_led` wraps LED classdev state and work. Module parameters `gkey_codes`, `recordkey_codes`, and `profilekey_codes` customize keycodes. `corsair_usage_to_gkey()` and `corsair_input_mapping()` translate G-keys, macro record, and profile usages. K90 LED/sysfs support is implemented by `k90_init_backlight()`, `k90_init_macro_functions()`, cleanup helpers, `k90_backlight_work()`, `k90_record_led_work()`, and sysfs `macro_mode`/`current_profile`. `corsair_event()` tracks macro record start/stop to update record LED state. `corsair_mouse_report_fixup()` corrects a bad logical maximum item on specific mouse interface descriptors.

Control flow: probe requires USB, allocates driver data, parses, starts HID, and on interface 0 initializes K90 macro and/or backlight facilities according to ID quirks. Input mapping consumes keyboard-page usages for G keys and special macro/profile controls, returning `-1` for unsupported special usages. LED brightness changes schedule USB vendor-control work. Sysfs reads/writes issue vendor USB control requests for macro mode and profile. Remove cleans macro and backlight resources before stopping HID.

State/persistence: driver state includes current LED brightness and K90 resource pointers. Hardware macro mode, profile, and backlight state may persist in the device firmware, but the driver itself only caches LED brightness. Keycode module parameter arrays are global runtime configuration.

Dependencies/integration: uses HID core, USB control transfers, LED classdev, sysfs attribute groups, Linux input mapping, and Corsair IDs. The mouse fixup depends on USB interface number to target the correct interface.

Risks: K90 support uses manual allocation and explicit cleanup; partial initialization must stay paired. LED work checks `removed` but no spinlock protects the flag, so teardown ordering and `cancel_work_sync()` matter. USB control message return conventions differ between reads and writes and are validated manually. Descriptor fixup is byte-offset based and comments contain historical typo context, so regression tests should focus on behavior not comments.

Test signals: verify G1-G18, macro record, and profile key mappings including module parameter overrides; K90 backlight LED class brightness get/set; record LED follows macro start/stop events; `macro_mode` and `current_profile` sysfs validation and USB errors; descriptor fixup only on interface 1 of the two mouse IDs; and cleanup after partial macro/backlight init failures.
