# sources/distributed-fs/ceph-client/drivers/video/backlight/lcd.c

## Purpose
This file implements the Linux LCD class abstraction used by low-level LCD panel drivers. It creates `/sys/class/lcd/*` devices, exposes power/contrast attributes, supports managed registration, and provides broadcast blank/mode notifications.

## Important APIs, Types, and Functions
Global `lcd_dev_list` tracks registered LCD devices under `lcd_dev_list_mutex`. `lcd_notify_blank_all()` and `lcd_notify_mode_change_all()` walk the list and call per-device ops after `controls_device` filtering. Sysfs handlers implement `lcd_power`, `contrast`, and `max_contrast`. `lcd_device_register()` and `lcd_device_unregister()` allocate/register/free `struct lcd_device`. `devm_lcd_device_register()` and `devm_lcd_device_unregister()` wrap registration in devres.

## Control Flow
The class is registered at `postcore_initcall()` so built-in LCD users can register later. `lcd_device_register()` allocates the device, initializes locks, sets class/parent/release/name/driver-data, stores ops, registers the device, then adds it to the global list. Unregister removes it from the list, clears `ops` under `ops_lock`, and unregisters the device. Sysfs reads/writes hold `ops_lock` while calling optional driver callbacks.

## State and Persistence
The only class-level state is the in-memory global list. Each LCD device carries properties, locks, ops pointer, and driver data. No state persists across reboot.

## Dependencies and Integration Points
The file depends on the device core, sysfs attribute groups, notifier-like exported helpers, mutex guard helpers, and `linux/lcd.h`. It is the integration point for panel drivers in this work item.

## Risks
Sysfs store paths ignore callback return values from `set_power()` and `set_contrast()` and return `count` if an op exists. Broadcast notifications call callbacks while holding the global list lock and each device ops lock, so callback reentrancy into registration paths would be hazardous. The class init warning says "backlight class" although it registers the LCD class.

## Test Signals
Test class registration, device register/unregister, devm release, sysfs power/contrast read-write with and without ops, broadcast blank/mode filtering, unregister racing with sysfs, and driver callbacks returning errors.
