# sources/distributed-fs/ceph-client/drivers/mfd/twl-core.c

## Purpose
`twl-core.c` is the central built-in I2C MFD core for TWL4030/TWL5030/TWL6030/TWL6032/TPS659x0 companion PMIC/audio chips. It creates regmaps for multiple I2C slave addresses, maps logical TWL module IDs to slave/base offsets, exports module-relative I2C read/write helpers, initializes clocks and IDCODE state, initializes chip IRQ handling, populates OF child devices, and supports TWL6030-class power-off.

## Important APIs, Types, And Functions
Private state is `struct twl_private`, containing readiness, IDCODE, class ID, module map, and per-slave `struct twl_client` regmaps. Exported functions are `twl_rev()`, `twl_i2c_write()`, `twl_i2c_read()`, `twl_set_regcache_bypass()`, `twl_get_type()`, `twl_get_version()`, and `twl_get_hfclk_rate()`. Major helpers are `twl_get_regmap()`, `twl_read_idcode_register()`, `clocks_init()`, `twl_remove()`, `twl6030_power_off()`, `twl_probe()`, `twl_suspend()`, and `twl_resume()`.

## Control Flow
The built-in I2C driver probes only with an OF node and only one global instance. Probe creates a platform device named `"twl"`, checks I2C functionality, allocates global state, selects TWL4030 or TWL6030 maps/configs from the I2C ID, creates dummy I2C clients for additional slave addresses, initializes each regmap, marks the core ready, programs clock configuration based on the `fck` clock, reads IDCODE on TWL4030-class chips, initializes the appropriate IRQ subsystem if the parent IRQ exists, applies TWL4030 pull-up/SmartReflex register tweaks, creates TWL6030/TWL6032 clock MFD cells and optional power-off callback, and calls `of_platform_populate()`.

## State, Persistence, And Dependencies
Global singleton `twl_priv` gates exported helper availability. Persistent hardware effects include PM master clock boot configuration, IDCODE unlock/relock, TWL4030 pull-up disable, SmartReflex enable, TWL6030 power-off writes, and child-driver register writes through exported helpers. Dependencies include I2C, regmap, clock framework, OF platform population, IRQ subsystems declared in `twl-core.h`, MFD core, and `linux/mfd/twl.h`.

## Integration Points
TWL child drivers use module IDs and exported helpers rather than direct I2C clients. `twl4030-irq.c` and TWL6030 IRQ support are called from here. `twl4030-audio.c` consumes `twl_get_hfclk_rate()` and module I/O helpers. `twl4030-power.c` uses PM master/receiver writes. OF auxdata maps `"ti,twl4030-gpio"` to `twl4030-gpio`.

## Risks
The singleton blocks multiple TWL devices. `twl_get_type()` and `twl_get_version()` assume `twl_priv` is valid, unlike safer read/write helpers. The platform device allocated in probe is not stored for normal successful removal. Probe error paths call `twl_remove()` and unregister the platform device, but successful remove does not unregister the platform device here. Exported read/write helpers return `-EPERM` before ready, so early child use must be ordered correctly.

## Test Signals
Test TWL4030/TWL5031/TWL6030/TWL6032 ID matching, dummy-client creation failure unwinding, exported read/write offset mapping for every module, regcache bypass, IDCODE read/unlock/relock, clock rates for 19.2/26/38.4 MHz and missing clock, IRQ init for both chip classes, OF child population, suspend/resume IRQ disable/enable, and TWL6030 power-off callback.
