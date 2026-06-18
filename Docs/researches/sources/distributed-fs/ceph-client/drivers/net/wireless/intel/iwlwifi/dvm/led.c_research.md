# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.c

## Purpose

`led.c` implements optional Linux LED-class integration for DVM devices. It registers a per-wiphy LED, supports radio-state or throughput-triggered modes, translates brightness/blink requests into firmware `REPLY_LEDS_CMD` commands, and compensates blink timings for MAC clock deviations.

## Important APIs, Types, and Functions

Exported functions are `iwlagn_led_enable()`, `iwl_leds_init()`, and `iwl_leds_exit()`. Local helpers include `iwl_blink_compensation()`, `iwl_send_led_cmd()`, `iwl_led_cmd()`, `iwl_led_brightness_set()`, and `iwl_led_blink_set()`. The static `iwl_blink[]` table maps throughput thresholds to blink periods for `ieee80211_create_tpt_led_trigger()`.

## Control Flow

`iwl_leds_init()` checks module LED mode, resolves default mode from device config, allocates a LED name based on the wiphy, installs brightness and blink callbacks, chooses a throughput or RF-state default trigger, registers the LED class device, and marks `priv->led_registered`. Brightness and blink callbacks call `iwl_led_cmd()`, which rejects requests when the device is not ready, avoids duplicate commands, maps `off == 0` to solid-on firmware semantics, applies hardware compensation to on/off values, sends an async LED host command, and caches the current blink values on success.

`iwlagn_led_enable()` directly turns on LED register control during device start. `iwl_leds_exit()` unregisters the LED and frees the allocated name only if registration succeeded.

## State and Persistence Behavior

Persistent software state includes `priv->led`, `priv->blink_on`, `priv->blink_off`, and `priv->led_registered`. Hardware state includes `CSR_LED_REG` and firmware LED command state. `iwl_send_led_cmd()` masks `CSR_LED_REG` down to BSM control bits before sending the command.

## Dependencies and Integration Points

The file depends on Linux LED class APIs, mac80211 LED triggers, iwlwifi module parameters, transport register access, firmware command wrappers, and `CONFIG_IWLWIFI_LEDS`. `mac80211.c` initializes and exits LED support during hardware registration/unregistration and enables the LED on mac80211 start.

## Risks and Edge Cases

LED commands are asynchronous and only gated by `STATUS_READY`; callers must tolerate failures during reset/rfkill. A zero compensation value logs an error and uses raw timing. Duplicate blink suppression relies on cached uncompensated values. Name allocation or LED registration failure leaves LED support disabled without failing device registration.

## Test Signals

Build with LEDs enabled and disabled, exercise `led_mode` values disable/default/blink/RF-state, verify registration cleanup on failure injection, confirm throughput trigger changes firmware blink commands, test brightness on/off during running device, and ensure no command is sent before `STATUS_READY`.
