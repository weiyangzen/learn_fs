# sources/distributed-fs/ceph-client/drivers/regulator/rt6160-regulator.c

Purpose: provides a Richtek RT6160/RT6166 buck-boost regulator driver with optional hardware enable GPIO, cached regmap power-down handling, voltage selection, mode, ramp delay, suspend voltage, and error flags.

Important APIs/types/functions: `struct rt6160_priv` stores descriptor, enable GPIO, regmap, software enable state, and device ID. `rt6160_enable()`/`disable()` control GPIO and regcache cache-only state. `rt6160_get_error_flags()` maps status bits for hot-die, under-voltage, over-current, thermal shutdown, and power-good failure. `rt6160_of_map_mode()` maps DT modes.

Control flow: probe reads VSEL polarity property, asserts optional enable GPIO, initializes regmap, validates vendor/device ID, fills descriptor min voltage based on RT6160 vs RT6166, selects active VSEL register, and registers the regulator. Disabling with GPIO marks regcache dirty/cache-only before powering hardware off; enabling reactivates hardware, exits cache-only mode, and synchronizes registers.

State and persistence: `enable_state` is software-owned and initialized true. Regmap cache preserves configuration across GPIO-controlled hardware disable. Hardware stores voltage, mode, ramp, and status while powered.

Dependencies and integration: depends on I2C, optional `enable` GPIO, property API, regcache, regulator framework, and OF regulator init data.

Risks and test signals: if no enable GPIO exists, `disable()` returns `-EINVAL` while `enable()` is a no-op, so consumers cannot software-disable. `get_mode()` returns raw I/O errors as regulator mode values. Tests should cover GPIO absent/present paths, regcache sync failure, vendor IDs, RT6166 min-voltage selection, VSEL active-low property, suspend voltage on inactive register, and error flag mapping.
