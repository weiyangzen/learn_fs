# sources/distributed-fs/ceph-client/drivers/leds/blink/leds-bcm63138.c

## Purpose
This platform driver controls the Broadcom BCM63138-family SoC LED hardware block, also used by related BCM49xx/68xx/63xx parts. It registers each firmware-described LED as a Linux LED class device with brightness and fixed-rate hardware blinking support.

## Important APIs, Types, and Functions
`struct bcm63138_leds` stores the device, MMIO base, and spinlock; `struct bcm63138_led` stores per-LED classdev state, pin number, and polarity. Register helpers are `bcm63138_leds_read()`, `bcm63138_leds_write()`, and `bcm63138_leds_update_bits()`. LED operations are `bcm63138_leds_brightness_set()` and `bcm63138_leds_blink_set()`. Probe and registration flow is in `bcm63138_leds_probe()` and `bcm63138_leds_create_led()`.

## Control Flow
Probe allocates private state, maps the MMIO resource, initializes global controller registers, optionally programs `brcm,serial-shift-bits`, disables hardware LED ownership, clears serial/parallel polarity, and iterates available child nodes. Each child must provide `reg`, may provide `active-low`, and is registered with `devm_led_classdev_register_ext()`. Brightness writes update `BCM63138_SW_DATA`; nonzero brightness programs one of four brightness registers, while zero also clears flash rate. Blink requests accept only equal on/off delays and map supported periods near 65, 140, 320, 640, and 1280 ms to hardware codes.

## State and Persistence
State is volatile and per platform device. The driver does not persist user settings across reboot or module unload. Hardware registers hold current brightness/blink state while the device is bound. Spinlock protection is used for read-modify-write sequences called from LED class callbacks.

## Dependencies and Integration Points
The driver depends on OF child nodes, `devm_platform_ioremap_resource()`, MMIO accessors, pinctrl defaults per LED, and LED class registration. It binds `brcm,bcm63138-leds` through a platform driver named `leds-bcm63xxx`.

## Risks and Edge Cases
`GENMASK(shift_bits - 1, 0)` assumes a nonzero valid `brcm,serial-shift-bits` value. Unsupported blink periods return `-EINVAL`; unequal delays are not approximated. LED child creation logs errors but does not fail the whole probe, so a partial LED set is possible. Pinctrl failure other than `-ENODEV` is only a warning after LED registration. Polarity and hardware-ownership register writes affect shared controller outputs globally.

## Test Signals
Use device-tree nodes with valid and invalid `reg` values, active-high and active-low LEDs, and optional pinctrl states. Validate sysfs brightness writes, fixed blink delays, rejection of unequal/unsupported blink delays, no races under concurrent trigger updates, and correct module binding on Broadcom OF compatibles.
