<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c

## Purpose
Registers the single OMAP1 I2C controller as an `omap_i2c` platform device and supports boot-command overrides for bus speed. It bridges board files and the generic `i2c-omap` driver by supplying fixed OMAP1 register, IRQ, mux, and IP-version data.

## Important APIs, Types, and Functions
Exports `omap_i2c_add_bus()`, `omap_register_i2c_bus()`, and `omap_register_i2c_bus_cmdline()`. Important state is `i2c_pdata[]`, the one-element `omap_i2c_devices[]`, `i2c_resources[]`, and the `OMAP_I2C_CMDLINE_SETUP` flag stored in `clkrate`.

## Control Flow
`omap_register_i2c_bus()` first registers `i2c_board_info`, records the default clock rate unless the command line already set one, clears the command-line marker, and calls `omap_i2c_add_bus()`. `omap_i2c_add_bus()` muxes SDA/SCL, fills MEM and IRQ resources, sets OMAP1 driver flags, attaches platform data, and registers the device. The `i2c_bus=` setup hook records deferred bus requests that `subsys_initcall` later materializes.

## State and Persistence Behavior
Persistent kernel state is the static platform-data array, the command-line marker bit, and registered platform devices. Hardware state includes muxed I2C pins and the driver's later register programming; this file itself does not retain runtime transfer state.

## Dependencies and Integration Points
Depends on the platform bus, `i2c_register_board_info()`, `platform_device_register()`, `INT_I2C`, OMAP1 mux entries `I2C_SDA`/`I2C_SCL`, and `linux/platform_data/i2c-omap.h` flag definitions.

## Risks
`bus_id > 1` returns `-EINVAL` even though the static pdata array has four entries, so OMAP1 effectively supports one controller here. Shared `i2c_resources[]` and `omap_i2c_devices[]` assume no duplicate registration. Bad `i2c_bus=` parsing silently ignores malformed options.

## Test Signals
Boot an OMAP1 config with and without `i2c_bus=1,<kHz>` and confirm one `omap_i2c` platform device, IRQ `INT_I2C`, MEM `0xfffb3800-0xfffb383f`, and expected `i2c-omap` probe flags. A negative test should pass `bus_id=2` or malformed command-line values and verify no stray controller registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c -->
