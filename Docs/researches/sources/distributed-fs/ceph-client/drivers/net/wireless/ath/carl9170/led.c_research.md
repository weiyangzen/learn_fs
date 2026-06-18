# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/led.c

## Purpose

`led.c` initializes AR9170 GPIO LED pins and, when `CONFIG_CARL9170_LEDS` is enabled, registers mac80211 LED class devices for TX and association indication. It translates LED trigger brightness changes into coalesced GPIO state updates.

## Important APIs, Types, and Functions

Always-built functions are `carl9170_led_set_state()` and `carl9170_led_init()`. Optional LED-class support adds `carl9170_led_update()`, `carl9170_led_set_brightness()`, `carl9170_led_register_led()`, `carl9170_led_unregister()`, and `carl9170_led_register()`. It uses per-device `ar->leds[]`, `ar->led_work`, and `AR9170_NUM_LEDS`.

## Control Flow

Initialization sets GPIO 0 and 1 as outputs and turns both off. With LED support enabled, registration initializes delayed work, registers LED 0 with the mac80211 TX trigger, and registers LED 1 with the association trigger unless the device has `CARL9170_ONE_LED`. Brightness callbacks update `last_state` and `toggled`, then schedule delayed work. The work function checks command acceptance, locks `ar->mutex`, derives the GPIO bitmask, writes `AR9170_GPIO_REG_PORT_DATA`, clears toggle counters, and reschedules itself if needed.

## State and Persistence Behavior

The file persists LED registration status, LED names, last brightness state, toggle counters, and delayed-work scheduling. Hardware state is the GPIO port type and port data register. Unregistration clears registration flags, resets toggle counters, unregisters class devices, and cancels delayed work synchronously.

## Dependencies and Integration Points

It depends on `cmd.h` register write helpers, `hw.h` GPIO constants, mac80211 LED trigger name helpers, Linux LED classdev, wiphy device naming, and the core device state predicate `IS_ACCEPTING_CMD()`.

## Risks and Edge Cases

Brightness callbacks can arrive while the device is stopping; the command-acceptance check prevents new hardware writes but delayed work must still be canceled during teardown. If LED 0 registration succeeds and LED 1 fails, registration unwinds through `carl9170_led_unregister()`. Brightness callbacks update counters without `ar->mutex`, so the fields must remain simple and race-tolerant.

## Test Signals

Build with and without `CONFIG_CARL9170_LEDS`. Verify GPIO type/data writes during register and stop paths. Check that TX trigger toggles LED 0, association trigger toggles LED 1 on two-LED devices, one-LED devices skip LED 1, failed LED registration unwinds cleanly, and stop/unregister cancels delayed work with LEDs off.
