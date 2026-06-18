# sources/distributed-fs/ceph-client/include/linux/backlight.h

## Purpose
Defines the kernel backlight class abstraction used by display, platform, firmware, and raw hardware drivers to expose brightness and power control to userspace and display-notification paths.

## Important APIs, types, and functions
- `enum backlight_update_reason`, `enum backlight_type`, and `enum backlight_scale` classify update source, control mechanism, and brightness scale.
- `struct backlight_ops` supplies `update_status()`, optional `get_brightness()`, and optional `controls_device()` callbacks.
- `struct backlight_properties` stores user brightness, maximum brightness, power, type, core state bits, and scale.
- `struct backlight_device` stores properties, locks, ops pointer, class device, list entry, and `use_count`.
- Registration and lookup APIs include `backlight_device_register()`, `devm_backlight_device_register()`, unregister variants, `backlight_device_get_by_name()`, `backlight_device_get_by_type()`, OF lookup helpers, and brightness/update helpers.

## Control flow and state
Drivers register a `backlight_device` with immutable maximum brightness and type. Userspace or display events mutate `props` and call `backlight_update_status()`, which serializes `ops->update_status()` under `update_lock`. `backlight_enable()` and `backlight_disable()` change power and blank state before invoking the callback. Drivers should call `backlight_get_brightness()` in `update_status()` so blank/suspend state maps to zero brightness.

## State and persistence behavior
State is runtime class-device state visible via `/sys/class/backlight`. Core state bits such as `BL_CORE_SUSPENDED` and `BL_CORE_FBBLANK` are owned by the core, not drivers. Device-managed registration ties lifetime to a parent device.

## Dependencies and integration points
Depends on device model, mutexes, types, OF support, and optional `CONFIG_BACKLIGHT_CLASS_DEVICE`. Integrates with framebuffer/display blank notifications, sysfs, platform and firmware display drivers, and device-managed resource cleanup.

## Risks
Drivers must not mutate core-owned state or use internal locks directly. `ops` can be NULL after driver unload, so callbacks are checked. Incorrect `controls_device()` can blank or unblank the wrong display. Brightness values must stay within `0..max_brightness`.

## Test signals
Test registration/unregistration, sysfs brightness and `bl_power`, suspend/resume when `BL_CORE_SUSPENDRESUME` is set, display blank notifications, OF lookup fallback, and driver unload while class device references exist.
