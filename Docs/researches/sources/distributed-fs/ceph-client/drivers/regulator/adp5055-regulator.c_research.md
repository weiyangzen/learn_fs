# sources/distributed-fs/ceph-client/drivers/regulator/adp5055-regulator.c

Purpose: I2C regulator driver for Analog Devices ADP5055, exposing three buck regulators with voltage selection, enable, active discharge, ramp delay, and power-save mode control.

Important APIs/types/functions: `struct adp5055` stores regmap, global timing, optional enable GPIOs, DVS limits, fast-transient settings, and power-good masks. `adp5055_of_parse_cb()` parses per-buck properties, `adp5055_parse_fw()` writes global/per-channel configuration, and `adp5055_set_mode()`/`get_mode()` control pulse-skipping mode bits.

Control flow: probe requires OF regulator init data, allocates state, initializes regmap, chooses each descriptor’s ramp delay table from `tset`, registers three regulators, then applies parsed firmware settings to DVS limit, enable-mode, OCP blanking, fast-transient, and power-good registers. Per-regulator OF callbacks run during registration and populate channel state.

State and persistence: driver state records GPIOs and parsed configuration; PMIC registers hold active voltage, enable mode, discharge, ramp, and DVS settings. The selected `adi,tset-us` is stored in memory and used to encode register values.

Dependencies and integration: depends on I2C, regmap access table for `0xd1..0xe0`, OF regulator parsing, GPIO descriptors, bitfield helpers, and regulator regmap ops.

Risks and test signals: `adi,tset-us` is parsed after descriptors are registered, so non-default timing may not affect the ramp-delay table exposed to regulator core. Error returns pass positive out-of-range values into `dev_err_probe()`. Tests should cover default and 20800 us `tset`, GPIO versus software enable, all DVS limit bounds, fast-transient string matching, mode bit shifts per channel, and probe deferral on GPIO/regmap errors.
