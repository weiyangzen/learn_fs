## sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-laptop.c

Purpose: Fujitsu Lifebook platform driver for ACPI brightness device `FUJ02B1` and hotkey/feature device `FUJ02E3`. It supports vendor backlight, input hotkeys, LED controls, platform status attributes, and battery charge-control extension.

Important APIs/types/functions: `call_fext_func()` evaluates the Fujitsu `FUNC` ACPI method with four integer arguments. `struct fujitsu_bl` owns brightness input/backlight state. `struct fujitsu_laptop` owns hotkey input, platform device, FIFO, flags, and battery charge-control status. Backlight code uses `GBLL/RBLL/SBLL/SBL2` plus `FUNC_BACKLIGHT` power control. Hotkey code reads `FUNC_BUTTONS` GIRB values and `FUNC_FLAGS` status/soft-key bits. LED classdevs implement logolamp, keyboard lamps, radio LED, and eco LED through `FUNC_LEDS` or `FUNC_FLAGS`. Battery hook exposes `charge_control_end_threshold`.

Control flow: init registers the brightness driver, platform status driver, and laptop driver. FUJ02B1 probe registers brightness input/backlight and notify handler when vendor backlight is selected. FUJ02E3 probe initializes FIFO, discards stale button entries, reads supported flags, syncs backlight power, registers input/LEDs/platform sysfs, installs notify handler, and optionally registers battery hook. Notify drains button events, tracks press/release using FIFO, updates flags, and reports soft keys.

State and persistence: brightness level and backlight power affect firmware. LED settings and charge thresholds persist according to firmware behavior. Runtime state includes FIFO of pressed scancodes, supported/current flags, global `fext`, and global `fujitsu_bl`.

Dependencies and integration: ACPI platform devices, input sparse-keymap, backlight, LED class, platform sysfs, kfifo, battery hook/power supply, DMI keymap overrides, ACPI video.

Risks: globals assume at most one FUJ02E3/FUJ02B1 pairing. FIFO overflow or missed release events can leave keys logically pressed. Charge-control validation clamps low values to 50. Test signals include DMI keymaps, brightness notifications, soft keys, LED set/get, lid/dock/radio attributes, battery threshold read/write, unsupported FUNC responses, and multi-device warning path.
