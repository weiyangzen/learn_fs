# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.h

## Purpose
`tsc200x-core.h` provides register addresses, command bits, default tuning constants, and exported interfaces shared by TSC2004/TSC2005 wrappers and the TSC200x core.

## Important APIs, Types, And Functions
The header defines command byte bits (`TSC200X_CMD_*`), register selector values, configuration register defaults (`TSC200X_CFR0_INITVALUE`, `CFR1`, `CFR2`), masks, default fuzz/resistance values, SPI speed, and pen-up timeout. It declares `tsc200x_regmap_config`, `tsc200x_pm_ops`, `tsc200x_groups`, and `tsc200x_probe()`.

## Control Flow
Bus-specific drivers include this header, create a regmap using the shared config, and call `tsc200x_probe()` with a bus command callback. PM and sysfs groups are wired into bus driver structures through these declarations.

## State And Persistence
The header defines constants only. Runtime state is allocated in `tsc200x-core.c`; persistent storage is not involved.

## Dependencies And Integration Points
It is the contract between I2C/SPI wrappers and the common core, and implicitly encodes controller datasheet register layout.

## Risks
Register stride, command bits, and writable masks must remain synchronized with `tsc200x_regmap_config`. Constants are shared across both TSC2004 and TSC2005, so variant-specific behavior should not be added here without care.

## Test Signals
Build both bus drivers, validate regmap addresses/flags on hardware or emulation, verify PM group linkage, and check scan configuration writes match expected datasheet defaults.
