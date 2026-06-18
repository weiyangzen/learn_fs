# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/led.c

## Purpose
This file implements optional p54 LED class integration. It registers association, TX, RX, and radio LEDs, coalesces brightness activity into firmware LED state, and unregisters LED devices during teardown.

## Important APIs, Types, and Functions
- `p54_init_leds()` initializes delayed work and registers four LED class devices.
- `p54_register_led()` creates names of the form `p54-<wiphy>::<name>` and attaches mac80211 LED triggers.
- `p54_led_brightness_set()` records trigger activity and schedules delayed update work.
- `p54_update_leds()` computes `softled_state`, calls `p54_set_leds()`, and reschedules for blink behavior.
- `p54_unregister_leds()` unregisters LEDs and cancels delayed work.

## Control Flow
When a mac80211 LED trigger sets brightness, the brightness callback increments a per-LED toggle counter and queues work. The work handler skips if the device mode is unspecified, sets bits for toggled LEDs, derives a blink delay based on activity, clears inactive bits, sends a firmware LED command, and reschedules if brightness is off but blinking should continue.

## State and Persistence Behavior
LED state lives in `priv->leds[]`, `priv->softled_state`, and `priv->led_work`. The firmware receives the current bitmask through `p54_set_leds()`. Registration state prevents double-registering and controls unregister cleanup.

## Dependencies and Integration Points
This file is compiled only with `CONFIG_P54_LEDS`. It depends on Linux LED class APIs, mac80211 trigger-name helpers, p54 common state, and firmware LED command support in `fwio.c`.

## Risks and Edge Cases
The TODO notes the driver does not derive actual LED count from EEPROM. Partial registration failure can leave earlier LEDs registered until common unregister cleanup. Updates while the device is down are skipped to avoid firmware commands after stop.

## Test Signals
Signals include LED class devices appearing, mac80211 triggers toggling firmware LEDs, clean unregister on module/device removal, and no work execution after stop.
