# sources/distributed-fs/ceph-client/include/linux/led-class-flash.h

Purpose: extends the LED class for camera/torch flash devices with strobe, flash brightness, timeout, duration, and fault reporting operations.

Important APIs and types: `LED_FAULT_*` bits mirror V4L2 flash faults. `struct led_flash_ops` supplies callbacks for brightness set/get, strobe set/get, timeout, fault, and duration. `struct led_flash_setting` holds min/max/step/current values. `struct led_classdev_flash` embeds a base `led_classdev`, ops, brightness/timeout/duration constraints, and flash sysfs groups. Registration helpers have regular and devm forms; inline and exported setters/getters implement the public control surface.

Control flow: a flash driver initializes constraints and callbacks, registers the flash LED, and class/sysfs/V4L2 bridge code calls setters/getters. `led_set_flash_strobe()` directly delegates to `ops->strobe_set`; optional getters return `-EINVAL` if unsupported.

State and persistence: state is in-memory class-device state plus hardware register state owned by the driver. Fault bits are read from hardware or cached by the driver; settings are not persisted by the class header.

Dependencies and integration points: depends on `leds.h` and device attributes; integrates LED class flash sysfs with V4L2 flash fault semantics.

Risks and test signals: risks include missing mandatory ops, mismatch with V4L2 fault bits, invalid constraint values, and races between torch/flash mode users. Test registration, sysfs attributes, devm cleanup, strobe on/off, brightness/timeout/duration bounds, fault reporting, and V4L2 flash integration.
