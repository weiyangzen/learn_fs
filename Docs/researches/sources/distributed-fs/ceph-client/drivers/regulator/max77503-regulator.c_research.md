# sources/distributed-fs/ceph-client/drivers/regulator/max77503-regulator.c

Purpose: provides a compact single-buck regulator driver for ADI/MAX77503 with voltage selection, current-limit switching, soft-start, active discharge, and enable control.

Important APIs/types/functions: `max77503_buck_ops` uses regulator core regmap helpers for enable, voltage selector, current limit, active discharge, and soft-start. `max77503_regulators_desc` defines the two-register hardware layout: `MAX77503_REG_CFG` for enable/current/soft-start/discharge and `MAX77503_REG_VOUT` for voltage.

Control flow: I2C probe initializes an 8-bit regmap, fills `regulator_config` with the device node and regmap, and registers the single static descriptor.

State and persistence: there is no private driver state after probe beyond devm-managed objects. Hardware registers persist the operating settings as long as the chip is powered.

Dependencies and integration: integrates I2C, regmap, OF matching (`adi,max77503`), and regulator framework generic operations.

Risks and test signals: the regmap max register is `0x2` while only registers `0x00` and `0x01` are used, so tests should check no accidental out-of-range access. Current-limit table has only two entries. Test enable bit, voltage range endpoint mapping, current limit selection, soft-start mask writes, active-discharge polarity, and missing DT constraints.
