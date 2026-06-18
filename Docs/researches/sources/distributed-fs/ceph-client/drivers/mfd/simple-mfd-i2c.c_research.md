# sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.c

## Purpose
`simple-mfd-i2c.c` is a generic I2C parent driver for simple register-mapped MFD devices. It creates a shared regmap, then either populates child DT nodes or registers static MFD cells for known compatible strings.

## Important APIs, Types, and Functions
The probe entry is `simple_mfd_i2c_probe()`. Default register format is `regmap_config_8r_8v`. Static cell arrays describe `sy7636a`, `max5970`/`max5978`, `max77705-battery`, and `spacemit,p1` children. `simple_mfd_i2c_of_match` maps compatible strings to optional `struct simple_mfd_data`.

## Control Flow
Probe fetches match data with `device_get_match_data()`, chooses a device-specific or default regmap config, and calls `devm_regmap_init_i2c()`. If no static MFD cells are configured, `devm_of_platform_populate()` creates child devices from firmware child nodes. Otherwise `devm_mfd_add_devices()` creates the declared cell list.

## State and Persistence
State is devm-managed: the parent regmap and child devices live for the I2C device lifetime. The driver itself keeps no global or persistent state.

## Dependencies and Integration Points
It integrates with OF matching, `devm_regmap_init_i2c()`, MFD cell registration, and child drivers that obtain the parent regmap through `dev_get_regmap(dev->parent, NULL)` or equivalent parent-device lookup.

## Risks and Edge Cases
Any compatible without match data gets an 8-bit register and 8-bit value map, which must match hardware. Static-cell devices ignore DT child-node enumeration. Cell names must match child platform drivers exactly.

## Test Signals
Probe success, shared parent regmap visibility from children, correct child list for each compatible, fallback DT population for simple CPLD/FPGA compatibles, and failure propagation from regmap or MFD registration are the main signals.
