# sources/distributed-fs/ceph-client/drivers/soc/cirrus/soc-ep93xx.c

Purpose: Cirrus EP93xx syscon-backed SoC driver. It registers SoC bus metadata and creates auxiliary child devices for pinctrl, clock, and reset controllers that need coordinated writes through software-locked system controller registers.

Important APIs and functions: `ep93xx_syscon_probe()` is used by `builtin_platform_driver_probe()`. `ep93xx_regmap_write()` and `ep93xx_regmap_update_bits()` wrap locked writes by writing `EP93XX_SWLOCK_MAGICK` before the target register update under a spinlock. `ep93xx_adev_alloc()`, `ep93xx_controller_register()`, and `ep93xx_unregister_adev()` allocate, add, and devm-clean auxiliary devices. `ep93xx_soc_revision()` and `ep93xx_get_soc_rev()` convert syscon revision bits to SoC metadata.

Control flow: probe obtains match-data model, gets a regmap from the syscon node, maps the resource, allocates `soc_device_attribute`, reads revision, registers the SoC device, then creates model-specific pinctrl, revision-specific clock, and reset auxiliary devices. It logs errors for child registration failures but returns success after attempting all children.

State and persistence: `ep93xx_map_info` holds the regmap, raw base, and shared spinlock passed to child devices. The registered `soc_device` and auxiliary devices persist for runtime consumers.

Dependencies and integration: depends on OF compatible strings for EP9301/9302/9307/9312/9315, MFD syscon regmap, `linux/soc/cirrus/ep93xx.h`, auxiliary bus, and SoC bus. Child drivers consume `struct ep93xx_regmap_adev` operations.

Risks and test signals: risks include swlock ordering bugs, child device lifetime errors, and model-to-pinctrl mapping mismatches. Test signals include SoC sysfs revision, auxiliary devices binding to pinctrl/clk/reset drivers, safe locked register writes under concurrent users, and E2 SSP clock variant selection.
