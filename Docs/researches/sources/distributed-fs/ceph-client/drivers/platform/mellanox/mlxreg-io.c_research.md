# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxreg-io.c

## Purpose
Generic Mellanox regmap I/O access driver that turns `mlxreg_core_platform_data` entries into hwmon sysfs files. It is used by board drivers to expose CPLD/FPGA registers, reset causes, control bits, and multi-register inventory values without bespoke sysfs code.

## Important APIs, Types, And Functions
`struct mlxreg_io_priv_data` stores platform data, hwmon groups, generated sensor attributes, reg value size, and a mutex. `mlxreg_io_get_reg()` is the core encoder/decoder for single-bit fields, full-register fields, masked bit sequences, and read-only multi-register values. `mlxreg_io_attr_show()` and `_store()` serialize access and perform regmap read/modify/write.

## Control Flow
Probe obtains platform data and regmap value width, initializes one attribute per data entry, registers the hwmon device `mlxreg_io`, initializes the mutex, and stores driver data. Reads call `mlxreg_io_get_reg()` in show mode and emit decimal values. Writes parse a bounded numeric buffer, compute the new register value from masks and bit offsets, and write back only the base register.

## State, Dependencies, Integration, Risks, Tests
State is limited to generated attributes and a mutex; hardware state lives in the supplied regmap. Dependencies include hwmon, regmap, `mlxreg` platform data, and board drivers such as `mlxreg-dpu`, `mlxreg-lc`, and `nvsw-sn2201`. Risks include fixed maximum 96 attributes, decimal-only sysfs output despite hardware bitfields, read-only multi-register fields not protected from writeable modes, subtle `rol32`/`ror32` bit numbering, and writing only the first register for multi-register definitions. Test signals include single-bit show/store, masked sequence show/store, multi-register read composition for 8-bit and 16-bit regmaps, invalid long writes, bus error propagation, and mutex-protected concurrent sysfs access.
