# sources/distributed-fs/ceph-client/drivers/regulator/tps6105x-regulator.c

Purpose: Platform child driver for the TPS61050/TPS61052 MFD boost converter when the chip is configured as a voltage regulator rather than LED/flash mode.

Important APIs/types/functions: `tps6105x_regulator_desc` describes a single boost regulator with four voltage table entries and regmap-backed enable, disable, is-enabled, get/set selector, and list-voltage operations. `tps6105x_regulator_probe` consumes the parent MFD platform data and regmap.

Control flow: probe gets the parent `struct tps6105x` from platform data, checks `pdata->mode`, returns success without registering anything unless the mode is `TPS6105X_MODE_VOLTAGE`, builds a regulator config using the parent I2C device, init data, OF node, and regmap, then registers one regulator.

State and persistence: all state is in the parent regmap, especially `TPS6105X_REG_0` mode and voltage fields. The driver keeps no private cache except the parent `tps6105x->regulator` pointer.

Dependencies and integration points: depends on the TPS6105x MFD core for I2C/regmap ownership and platform data. Regulator consumers see `tps6105x-boost`; OF matching uses child name `regulator`.

Risks: probe assumes parent platform data and `tps6105x->pdata` are valid. Returning success when not in voltage mode is intentional but means no regulator appears. The voltage table contains two 5 V selectors, so selector-specific tests should not assume voltage uniqueness.

Test signals: MFD mode gating, successful regulator registration in voltage mode, enable/mode bit programming, selector round trips for duplicate 5 V entries, and missing parent-data failure coverage.
