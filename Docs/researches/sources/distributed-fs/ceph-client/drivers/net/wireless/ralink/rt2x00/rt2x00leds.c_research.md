# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.c

## Purpose
Implements common LED class integration for rt2x00 radio, association, activity, and link-quality LEDs. It maps driver state and RSSI to LED brightness and handles registration, unregister, suspend, and resume.

## Important APIs, Types, And Functions
Exports `rt2x00leds_led_quality()`, `rt2x00led_led_activity()`, `rt2x00leds_led_assoc()`, `rt2x00leds_led_radio()`, `rt2x00leds_register()`, `rt2x00leds_unregister()`, `rt2x00leds_suspend()`, and `rt2x00leds_resume()`. Private helpers register/unregister individual `struct rt2x00_led` instances and perform simple full/off brightness changes.

## Control Flow
Quality LED updates add `rt2x00dev->rssi_offset`, bucket RSSI into six levels, and set brightness to a nonzero scaled value. Activity, association, and radio helpers set full/off brightness if the LED type matches and is registered. Registration builds names from driver name and phy name, registers initialized LED objects, and sets a default radio blink period if supported. Failure unwinds all LEDs. Suspend calls `led_classdev_suspend()` and turns LEDs off. Resume calls `led_classdev_resume()` and turns LEDs off again to clear hardware state.

## State And Persistence
LED registration state lives in `rt2x00_dev` members `led_radio`, `led_assoc`, and `led_qual`, with `LED_INITIALIZED` and `LED_REGISTERED` flags. Brightness is cached in `led_classdev.brightness`. LED state is not persistent across unregister/remove.

## Dependencies And Integration Points
Depends on `CONFIG_RT2X00_LIB_LEDS`, Linux LED class, wiphy device naming, chip code that initializes LED objects and brightness callbacks, link tuner RSSI updates, radio enable/disable paths, and firmware load LED reset.

## Risks
Brightness callbacks are chip-specific and may access hardware; unregister avoids setting off when LED is suspended but other paths assume access is safe. The registration name buffer is 36 bytes, so long driver/phy names can be truncated. Quality brightness never emits `LED_OFF` by design to avoid chip divisions, which may surprise users expecting zero for weak RSSI.

## Test Signals
LED class entries appear with expected names, radio and association state changes toggle LEDs, link quality changes brightness buckets, default blink is applied, suspend/resume leaves LEDs off, registration failure unwinds cleanly, and remove does not touch inaccessible hardware while suspended.
