# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.c

## Purpose
`led.c` connects `brcmsmac` radio LED support to Linux LED and GPIO subsystems. It discovers the board-defined radio LED GPIO from SPROM fields, requests the line from the BCMA chipcommon GPIO controller, registers an LED class device, and lets the mac80211 radio LED trigger drive the GPIO.

## Important APIs, Types, and Functions
- `BRCMS_LED_NO`, `BRCMS_LED_BEH_MASK`, `BRCMS_LED_AL_MASK`, and `BRCMS_LED_RADIO` describe SPROM LED scanning and polarity.
- `brcms_radio_led_ctrl()` writes the stored GPIO descriptor when present.
- `brcms_led_brightness_set()` is the LED class callback and maps `struct led_classdev` back to `struct brcms_info`.
- `brcms_led_register()` scans SPROM GPIO0-3 entries, finds radio behavior, honors active-low polarity, requests the GPIO with `gpiochip_request_own_desc()`, builds `brcmsmac-%s:radio`, assigns the mac80211 radio trigger, and registers `wl->led_dev`.
- `brcms_led_unregister()` unregisters the LED class device and releases the owned GPIO descriptor.

## Control Flow
Probe calls `brcms_led_register()` after core attach. Registration exits with `-ENODEV` when SPROM has no radio LED. Otherwise it requests the selected GPIO as output-low, sets LED class fields, and registers the LED on the wiphy device. At runtime, LED trigger brightness changes call `brcms_led_brightness_set()`, which writes logical 1 or 0 through the GPIO descriptor. Remove calls `brcms_led_unregister()` before mac80211 hardware teardown.

## State and Persistence
Runtime state lives in `wl->radio_led.name`, `wl->radio_led.gpiod`, and `wl->led_dev`. SPROM GPIO behavior is persistent board configuration, but this file only reads it. No driver state is written to disk.

## Dependencies and Integration Points
This file depends on mac80211 LED trigger naming, Linux LED class APIs, GPIO descriptor/chip APIs, BCMA chipcommon GPIO, SSB SPROM fields, wiphy device/logging helpers, `mac80211_if.h`, and the public declarations in `led.h`. `mac80211_if.c` owns probe/remove calls.

## Risks and Edge Cases
- Probe ignores LED registration errors, so LED setup is optional but failures require log inspection.
- If LED class registration fails after GPIO request, the GPIO remains stored and is later freed by unregister, but the local error path does not immediately release it.
- Only the first radio LED among GPIO0-3 is used.
- LED names can be truncated to the fixed 32-byte buffer.
- The brightness callback assumes `led_dev` is embedded in `struct brcms_info`.

## Test Signals
Build with and without `CONFIG_BRCMSMAC_LEDS`. Test SPROM configurations for no LED, active-high radio LED, and active-low radio LED. Verify `/sys/class/leds/brcmsmac-*:radio`, default trigger behavior, GPIO toggling, GPIO request failure, LED registration failure, and clean remove/unload.
