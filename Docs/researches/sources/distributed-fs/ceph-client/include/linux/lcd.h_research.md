# sources/distributed-fs/ceph-client/include/linux/lcd.h

Purpose: defines the LCD class-device abstraction for low-level panel power, contrast, mode, and display-notification control.

Important APIs and types: `struct lcd_ops` exposes `get_power`, `set_power`, `get_contrast`, `set_contrast`, `set_mode`, and optional `controls_device`. `struct lcd_device` embeds properties, ops/update locks, a list entry, and a device. `struct lcd_platform_data` carries reset/power callbacks, bootloader state, delays, and private data. Registration APIs include regular and devm variants; notification helpers broadcast blank and mode changes when `CONFIG_LCD_CLASS_DEVICE` is reachable.

Control flow: drivers register an `lcd_device` with ops, display/backlight code calls `lcd_set_power()` or notification helpers, and the class serializes `set_power()` through `update_lock` while protecting ops lifetime with `ops_lock`.

State and persistence: state is kernel device-model state plus driver-private panel data. Power/contrast changes affect hardware but are not persisted by this header.

Dependencies and integration points: depends on device model and mutexes; integrates framebuffer/display blanking, panel drivers, and platform data.

Risks and test signals: risks include calling ops after module unload, incorrect lock use, deprecated reduced-power values, and display matching errors. Test registration/unregistration, devm cleanup, blank/mode notifications, concurrent power changes, and module unload while userspace sysfs accesses exist.
