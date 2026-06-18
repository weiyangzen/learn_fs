# sources/distributed-fs/ceph-client/drivers/power/reset/vexpress-poweroff.c

## Purpose
ARM Versatile Express config-bus reset/shutdown/reboot driver.

## Important APIs, Types, and Functions
global poweroff/restart devices, restart notifier refcount, sysfs `active` selector, `vexpress_reset_do()`, and platform probe.

## Control Flow
probe initializes vexpress config regmap and dispatches by compatible: shutdown installs `pm_power_off`, reset/reboot register restart handler and optional active sysfs control. Callback writes zero to config function register and waits.

## State and Persistence Behavior
global selected devices and notifier refcount persist; sysfs `active` changes which reset device is used; config writes are consumed by platform firmware.

## Dependencies and Integration Points
VEXPRESS_CONFIG regmap, OF/property match data, legacy poweroff, restart notifier, sysfs.

## Risks and Edge Cases
global mutable active device can be changed by userspace; no remove path for built-in driver; poweroff and restart devices are singleton pointers.

## Test Signals
VExpress reset/shutdown/reboot compatibles, sysfs active switching, config write failure, and board/emulator reset.
