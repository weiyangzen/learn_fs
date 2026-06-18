# sources/distributed-fs/ceph-client/drivers/leds/led-class-flash.c

## Purpose
Provides the LED flash-class interface layered on top of `struct led_classdev`. It adds sysfs controls for flash strobe, flash brightness, flash timeout, and fault reporting, and exports registration and setting helpers for flash-capable LED drivers.

## Important APIs, Types, And Functions
The central public APIs are `led_classdev_flash_register_ext`, `led_classdev_flash_unregister`, `devm_led_classdev_flash_register_ext`, `devm_led_classdev_flash_unregister`, `led_set_flash_timeout`, `led_set_flash_brightness`, `led_update_flash_brightness`, `led_set_flash_duration`, and `led_get_flash_fault`.

`struct led_flash_ops` supplied by drivers provides `strobe_set`, optional `strobe_get`, `flash_brightness_set`, `flash_brightness_get`, `timeout_set`, `duration_set`, and `fault_get`. `struct led_flash_setting` values are clamped/aligned by `led_clamp_align`.

## Control Flow
Registration validates flash-capable devices: if `LED_DEV_CAP_FLASH` is set, the underlying classdev must have `brightness_set_blocking`, flash ops must exist, and `strobe_set` is required. It then attaches a flash resume callback, selects sysfs attribute groups based on available ops, and calls `led_classdev_register_ext`.

Sysfs stores acquire `led_access`, reject disabled sysfs, parse numeric input, and route to the exported setting helpers. Setting helpers update the cached `led_flash_setting`, clamp and align it to min/max/step, then call the driver operation unless the LED class device is suspended. Fault display calls `fault_get` and formats generic LED fault names.

## State And Persistence
Persistent state is held in the caller-owned `struct led_classdev_flash`: cached brightness, timeout, and duration settings plus operation pointers. The class does not store hardware state itself. On LED resume, `led_flash_resume` reapplies cached flash brightness and timeout to the hardware.

## Dependencies And Integration Points
Depends on the LED core class, device attributes, devres, and `linux/led-class-flash.h`. It integrates with flash LED drivers and with userspace through the LED sysfs ABI. Camera-facing integration is indirect through drivers that also register V4L2 flash objects.

## Risks
The operation macros assume `fled_cdev->ops` is valid when optional sysfs groups are created. Fault formatting depends on `LED_NUM_FLASH_FAULTS` matching the `led_flash_fault_names` table. `sprintf` use is older style and bounded only by the small fixed fault-name set. Suspended devices silently cache values without programming hardware, so resume reapplication is essential.

## Test Signals
Test by registering fake or real flash LEDs with different operation sets and confirming only supported sysfs attributes appear. Store paths should clamp/align values and reject invalid strobe values. Suspend/resume should restore cached flash brightness and timeout. Fault injection should display the expected generic names.
