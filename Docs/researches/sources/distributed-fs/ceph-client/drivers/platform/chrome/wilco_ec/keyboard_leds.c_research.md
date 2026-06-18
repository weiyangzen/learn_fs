<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c

## Purpose

This file implements the Wilco EC keyboard-backlight LED support used by the core Wilco driver. It detects EC keyboard-backlight capability, initializes PWM brightness mode, and registers a LED class device.

## Important APIs, Types, And Functions

`struct wilco_keyboard_leds` stores the EC pointer and LED classdev. `struct wilco_keyboard_leds_msg` is the packed legacy EC command payload for command `0x75`. `send_kbbl_msg()` sends a Wilco legacy mailbox command. `kbbl_exist()` probes support, `kbbl_init()` reads current state and forces PWM mode if needed, `set_kbbl()` sets brightness, and `wilco_keyboard_leds_init()` registers `platform::kbd_backlight`.

## Control Flow

Core probe calls `wilco_keyboard_leds_init()`. The helper first sends `GET_FEATURES`; status `0xff` means no keyboard LED support and probe continues without an LED. If present, it allocates LED state, initializes brightness from EC state or sets default brightness zero if EC is not in PWM mode, and registers a blocking brightness setter.

## State And Persistence

Kernel state is devm-managed LED classdev data. Brightness and mode live in EC firmware; the driver updates brightness on set and initializes PWM state during probe if needed. LED core handles suspend/resume flag behavior.

## Dependencies And Integration Points

It depends on Wilco mailbox commands, LED class support, and the core Wilco EC device. It is linked into the core `wilco_ec` module.

## Risks

Brightness values are passed as percentages 0-100 and rely on LED core bounds. Support detection treats any status other than `0xff` as present. If BIOS left the EC in a non-PWM mode, probe changes brightness to zero.

## Test Signals

Test feature-present and feature-absent EC responses, PWM-mode initialization, non-PWM fallback to zero, brightness set command failures, LED registration and removal through devm, and suspend/resume LED behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c -->
