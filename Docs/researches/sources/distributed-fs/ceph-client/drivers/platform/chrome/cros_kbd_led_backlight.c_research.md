<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c

## Purpose

This driver registers a ChromeOS keyboard-backlight LED class device. It supports two transport models: ACPI methods for legacy devices and Chrome EC PWM commands when instantiated as a Chrome EC MFD child.

## Important APIs, Types, And Functions

`struct keyboard_led` wraps `struct led_classdev` plus optional `struct cros_ec_device`. `struct keyboard_led_drvdata` selects init, get, set, blocking-set, and maximum brightness operations. The ACPI backend uses `\_SB.KBLT.KBQC` and `\_SB.KBLT.KBCM`; the EC backend uses `EC_CMD_PWM_GET_KEYBOARD_BACKLIGHT` and `EC_CMD_PWM_SET_KEYBOARD_BACKLIGHT`. `keyboard_led_probe()` chooses backend data and registers `chromeos::kbd_backlight`.

## Control Flow

When the platform device is an MFD cell, probe uses the EC PWM backend and stores the parent Chrome EC pointer. Otherwise it obtains match data from ACPI ID `GOOG0002`. Probe initializes the backend, populates LED callbacks and flags, then registers the LED. ACPI brightness set is nonblocking and calls ACPI directly; EC brightness set is blocking and sends a host command.

## State And Persistence

The driver keeps only the LED classdev and EC pointer. Actual brightness state is stored by ACPI firmware or EC PWM state. The LED core handles suspend/resume because the classdev sets `LED_CORE_SUSPENDRESUME`.

## Dependencies And Integration Points

It integrates with the LED subsystem, ACPI, Chrome EC MFD devices, and Chrome EC PWM commands. The device ID is `cros-keyboard-leds`, with ACPI match data for `GOOG0002`.

## Risks

The EC PWM backend is compiled to an empty drvdata when `CONFIG_MFD_CROS_EC_DEV` is disabled; an MFD-instantiated device would then lack callbacks and useful max brightness. Duplicate LED registration returns `-ENODEV` on `-EEXIST`, assuming another mechanism already bound the same LED. ACPI method paths are hard-coded.

## Test Signals

Test LED registration name, ACPI get/set calls, EC PWM get/set commands, max brightness clamping through LED core, duplicate registration handling, suspend/resume brightness restore, and behavior with/without `CONFIG_MFD_CROS_EC_DEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c -->
