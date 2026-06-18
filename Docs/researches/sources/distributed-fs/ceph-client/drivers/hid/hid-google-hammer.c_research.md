# sources/distributed-fs/ceph-client/drivers/hid/hid-google-hammer.c

Supports Google Hammer/Whiskers ChromeOS base keyboards. It combines a Chrome EC platform driver for base attach state with a HID driver for keyboard folded events, keyboard backlight, and Vivaldi function-row metadata.

`struct cbas_ec` stores the shared tablet-mode input device, base present/folded state, and EC notifier. `cbas_ec_query_base()` sends `EC_CMD_MKBP_INFO`; `cbas_ec_notify()` handles EC switch events; `cbas_ec_probe()` registers `SW_TABLET_MODE`. `struct hammer_kbd_leds` backs the LED class device; `hammer_kbd_brightness_set_blocking()` sends HID output reports. `hammer_input_mapping()` suppresses the vendor folded usage from normal input, while `hammer_event()` and `hammer_folded_event()` combine folded state with EC base state.

Module init registers the EC platform driver before the HID driver. EC probe seeds base state and subscribes to notifier events. HID probe starts hardware, enables always-polling for folded-report devices, reads initial folded state, and registers backlight when supported. Remove closes polling and forces tablet mode when a base keyboard disappears.

Shared runtime state is global `cbas_ec`, protected by spinlock and registration mutex. LED brightness is live hardware state, not persisted. Dependencies include HID core, Chrome EC APIs, platform bus, ACPI/OF, input switches, LED class, Vivaldi helpers, and Google IDs.

Risks include one-global-device assumptions, EC/HID race handling, fallback output-report paths, and initial folded-state layout assumptions. Test signals include EC attach/detach, folded reports, disconnect behavior, backlight writes, Vivaldi attributes, and suspend/resume state refresh.
