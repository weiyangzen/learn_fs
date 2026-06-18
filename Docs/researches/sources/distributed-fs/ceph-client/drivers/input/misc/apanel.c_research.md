<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c

Purpose: Fujitsu LifeBook application-panel driver for SMBus-accessible application/CD buttons and optional mail LED discovered from a BIOS signature.

Important APIs/types/functions: `apanel_init()` maps the 0xF0000 BIOS area, scans for `FJKEYINF`, records device-chip capabilities, and registers the I2C driver. `apanel_probe()` creates a polled input device, keymap, and optional LED class device. `apanel_poll()` reads a word from SMBus, clears the latch by writing zero, and emits press-release key events. `mail_led_set()` writes the LED bit.

Control flow and state: module init discovers one SMBus slave and feature set, then I2C probe clears the command register and registers input polling at 1000 ms. Polling decodes bit positions into `KEY_MAIL`, browser/program keys, and CD controls.

State and persistence behavior: static `device_chip[]` persists BIOS-discovered feature support for module lifetime. Input keymap is per-device. Mail LED state is hardware-backed and forced off during shutdown.

Dependencies and integration points: uses low BIOS memory mapping, I2C SMBus word accesses, input polling, LED class, and DMI aliases for Fujitsu LifeBook systems.

Risks: BIOS parsing trusts legacy table layout and supports only one SMBus slave. SMBus read errors are silently ignored in polling. The driver uses legacy platform discovery rather than firmware nodes.

Test signals: test BIOS signature absent/present, duplicate/unknown table entries, app-only and app+CD key maps, LED registration and shutdown-off behavior, and polling under SMBus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c -->
