# sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.h

Purpose: public in-driver contract between LP55xx chip-specific drivers and the shared LP55xx implementation.

Important APIs/types/functions: defines `LP55xx_BYTES_PER_PAGE`, engine index/mode enums, sysfs attribute-generation macros, `struct lp55xx_reg`, `struct lp55xx_device_config`, `struct lp55xx_engine`, `struct lp55xx_chip`, and `struct lp55xx_led`. It declares all common register, engine, brightness, current, probe/remove, and sysfs helper exports.

Control flow: chip drivers include this header, instantiate a `lp55xx_device_config`, use macros such as `LP55XX_DEV_ATTR_ENGINE_MODE()` to generate sysfs callbacks, and pass common `lp55xx_probe`/`lp55xx_remove` as their I2C driver hooks.

State and persistence: the header defines the in-memory state model but stores no data itself. Persistent behavior is determined by chip-specific register callbacks and hardware state.

Dependencies and integration: depends on `linux/led-class-multicolor.h` and platform data types from the C file's include graph. It is tightly coupled to LED class devices, firmware-backed engine programming, I2C client ownership, and chip-specific register maps.

Risks: the config structure is a soft ABI inside the driver family; missing function pointers or wrong register shifts/masks produce runtime hardware corruption rather than compile-time errors. Attribute macros assume common helper names and engine numbering from 1 to 3.

Test signals: build all LP55xx chip drivers, validate each config initializes every required register/callback, and exercise generated sysfs attributes for all engines and master faders on chips that expose them.
