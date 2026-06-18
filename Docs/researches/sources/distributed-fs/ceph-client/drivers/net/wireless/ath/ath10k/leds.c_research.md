# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.c

## Purpose

`leds.c` implements optional Linux LED class integration for ath10k devices with a firmware-controlled GPIO LED pin. It registers a per-wiphy LED class device, configures the target GPIO at start, and translates brightness changes into WMI GPIO output commands.

## Important APIs, Types, and Functions

- `ath10k_leds_register()` creates the LED name `ath10k-<wiphy>`, sets active-low/default-state metadata, assigns `brightness_set_blocking`, and registers `ar->leds.cdev`.
- `ath10k_leds_start()` configures `hw_params.led_pin` through WMI GPIO config/output, used after firmware start or restart.
- `ath10k_leds_unregister()` unregisters the LED class device.
- `ath10k_leds_set_brightness_blocking()` is the LED core callback and writes GPIO output when the device is ON.

## Control Flow

All public functions no-op when `ar->hw_params.led_pin == 0`, treating zero as unsupported. Registration fills label and `gpio_led`/`led_classdev` fields, then calls `led_classdev_register()` on the wiphy device. Start reconfigures the GPIO with no pull and disabled interrupt, then writes output high; comments note firmware can reset GPIO configuration, especially on QCA9984/QCA99XX. Brightness changes acquire `conf_mutex`, ignore requests unless the device state is `ATH10K_STATE_ON`, compute active-low GPIO state as `(brightness != LED_OFF) ^ active_low`, store it in `ar->leds.gpio_state_pin`, and call `ath10k_wmi_gpio_output()`.

## State and Persistence Behavior

State lives in `ar->leds`: label buffer, `wifi_led` metadata, `cdev`, and last `gpio_state_pin`. Registration persists with the LED subsystem until unregister. GPIO configuration persists in target firmware/hardware only until firmware or device reset, so `ath10k_leds_start()` reapplies it after start paths. No disk persistence exists.

## Dependencies and Integration Points

The file depends on Linux LED class APIs, wiphy device naming, ath10k core state, WMI GPIO config/output commands, and `hw_params.led_pin`. It is compiled only when `CONFIG_ATH10K_LEDS` enables the declarations in `leds.h`. It integrates with driver start/stop paths that call register/start/unregister.

## Risks

- LED support is keyed on `led_pin == 0`, so hardware using GPIO 0 as a valid LED would be impossible without changing the sentinel.
- Brightness writes while the device is not ON are silently ignored; callers rely on later start/reconfiguration to restore state.
- `ath10k_leds_start()` ignores return values from WMI GPIO operations and always returns success.
- Active-low is hard-coded to 1 in registration; board-specific polarity must be represented elsewhere or this may invert behavior.

## Test Signals

Useful tests include `CONFIG_ATH10K_LEDS=y/n` builds, register/start/unregister with `led_pin == 0`, LED class registration failure propagation, brightness OFF/non-OFF transitions with active-low polarity, writes ignored when `ar->state` is not ON, firmware restart calling `ath10k_leds_start()`, and WMI GPIO command tracing to confirm pin/config/output values.
