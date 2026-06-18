# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt8515.c

## Purpose
This platform driver supports the Richtek RT8515 GPIO-driven flash/torch LED controller found on some phones. It approximates brightness through GPIO pulse counts, enforces flash timeout with a kernel timer, and can expose a V4L2 flash device.

## Important APIs, Types, and Functions
`struct rt8515` stores the flash class device, V4L2 handle, mutex, optional regulator pointer, flash/torch GPIOs, powerdown timer, timeout, and computed intensity limits. GPIO helpers are `rt8515_gpio_led_off()` and `rt8515_gpio_brightness_commit()`. LED operations are `rt8515_led_brightness_set()`, `rt8515_led_flash_strobe_set()`, `rt8515_led_flash_strobe_get()`, and `rt8515_led_flash_timeout_set()`. Configuration uses `rt8515_determine_max_intensity()`.

## Control Flow
Probe gets `enf` and `ent` GPIOs, reads the child LED node, computes flash and torch intensity caps from DT resistor values and max microamp properties, initializes a timer and LED flash timeout settings, registers the flash LED class device, and optionally initializes V4L2 flash. Torch brightness pulses the torch GPIO for intermediate levels or drives it high for max. Flash strobe pulses the flash GPIO for configured max flash intensity and arms a timer to turn the LED off.

## State and Persistence
The timer represents active flash state; `strobe_get()` reports whether it is pending. Brightness and timeout settings are volatile. The driver destroys the timer and mutex on remove. The regulator member exists but is not acquired or used in this source.

## Dependencies and Integration Points
The driver depends on two GPIO descriptors, firmware resistor properties `richtek,rfs-ohms` and `richtek,rts-ohms`, child current/timeout properties, LED flash class, and optional V4L2 flash. It binds `richtek,rt8515`.

## Risks and Edge Cases
There is no datasheet-backed register interface, so brightness pulse behavior is inferred and hardware-sensitive. `rt8515_determine_max_intensity()` can compute intensity values beyond the hardware maximum or below useful range if DT values are inconsistent; it does not clamp to `hw_max`. Strobe-on does not explicitly clear torch first beyond using the flash GPIO pulses. The optional V4L2 init failure logs but continues, leaving `rt->v4l2_flash` as an error pointer; remove must tolerate this through the conditional helper path.

## Test Signals
Use GPIO tracing or a scope to validate pulse counts and off sequencing. Test resistor/current DT combinations, torch levels, flash timeout auto-off, manual strobe off, V4L2 registration failure handling, and removal while timer is pending.
