<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h

## Purpose
Provides the OMAP1 board-facing declarations for I2C controller registration while compiling to harmless stubs when `CONFIG_I2C_OMAP` is disabled or modularly unavailable.

## Important APIs, Types, and Functions
Declares `struct i2c_board_info`, `struct omap_i2c_bus_platform_data`, `omap_i2c_add_bus()`, `omap_register_i2c_bus()`, and `omap_register_i2c_bus_cmdline()`. The enabled path exposes real functions; the disabled path returns success from inline stubs.

## Control Flow
There is no runtime flow in the header. Its control path is compile-time selection based on `CONFIG_I2C_OMAP` or `CONFIG_I2C_OMAP_MODULE`, allowing board code to call registration helpers without open-coding `#ifdef` blocks.

## State and Persistence Behavior
The header owns no state. It defines the call contract that lets `i2c.c` maintain command-line and platform-device state.

## Dependencies and Integration Points
Integrates OMAP1 board files with the I2C core and `i2c-omap` platform data. It relies on `u32` being visible from includers or earlier kernel headers.

## Risks
Disabled stubs return `0`, so board code cannot tell that no I2C device was registered. This is intentional for optional subsystem builds but can hide missing config dependencies in board bring-up.

## Test Signals
Compile OMAP1 with `CONFIG_I2C_OMAP=y`, `m`, and `n`; board files should build in all cases and only enabled builds should produce registered platform devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h -->
