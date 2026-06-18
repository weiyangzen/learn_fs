# sources/distributed-fs/ceph-client/drivers/leds/led-class-multicolor.c

## Purpose
Implements the multicolor LED class wrapper. It exposes per-subLED color indexes and intensity weights through sysfs, calculates channel brightness components from aggregate brightness, and registers `struct led_classdev_mc` as a normal LED class device with multicolor metadata.

## Important APIs, Types, And Functions
The exported APIs are `led_mc_calc_color_components`, `led_classdev_multicolor_register_ext`, `led_classdev_multicolor_unregister`, `devm_led_classdev_multicolor_register_ext`, and `devm_led_classdev_multicolor_unregister`.

`multi_intensity` accepts one unsigned value per subLED and updates `mcled_cdev->subled_info[i].intensity`. `multi_index` prints color names from `led_get_color_name` for each subLED color index.

## Control Flow
Registration validates the multicolor classdev pointer, requires `num_colors > 0`, rejects more than `LED_COLOR_ID_MAX`, sets `LED_MULTI_COLOR`, attaches the multicolor sysfs groups, and calls `led_classdev_register_ext`.

Brightness calculation multiplies the aggregate brightness by each subLED intensity and divides by max brightness with rounding. Updating `multi_intensity` parses exactly `num_colors` integers, stores them under `led_access`, and if software blinking is not active, reapplies the current brightness so the driver callback sees refreshed subLED component brightness.

## State And Persistence
State lives in the driver-owned `struct led_classdev_mc` and its `subled_info` array. This file mutates only intensity and calculated brightness fields. Devres wrappers keep unregister tied to parent-device lifetime.

## Dependencies And Integration Points
Depends on `linux/led-class-multicolor.h`, the base LED class, device attributes, and `led_get_color_name` from the LED core. Drivers such as BlinkM use this class to expose one RGB LED instead of separate red/green/blue class devices.

## Risks
`multi_intensity_store` does not explicitly clamp intensity values to max brightness; component calculation can therefore produce values larger than expected if userspace writes large intensities and a driver does not constrain them. `multi_index_show` assumes valid color indexes; invalid driver data can yield null names. The parser is strict about extra trailing data.

## Test Signals
Register a multicolor LED and confirm `multi_index`, `multi_intensity`, and normal brightness behavior. Tests should update intensity with valid and invalid cardinality, check recalculated subLED brightness, and verify triggers using `led_mc_set_brightness` honor color count checks.
