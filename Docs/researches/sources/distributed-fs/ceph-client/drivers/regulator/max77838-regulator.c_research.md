# sources/distributed-fs/ceph-client/drivers/regulator/max77838-regulator.c

Purpose: standalone I2C regulator driver for MAX77838 PMIC, exposing four LDOs and one buck with linear voltage controls and active discharge.

Important APIs/types/functions: `MAX77838_LDO()` and `MAX77838_BUCK_DESC` build static descriptors. `max77838_regulator_ops` delegates enable, voltage, and active-discharge operations to regmap helpers. `max77838_read_device_id()` performs a diagnostic read of `MAX77838_REG_DEVICE_ID`.

Control flow: probe allocates info, initializes an 8-bit regmap through the buck VOUT register, registers five regulators, then reads the device ID.

State and persistence: the only private runtime state is the regmap pointer. Voltage, enable, and discharge settings live in hardware registers.

Dependencies and integration: depends on I2C, regmap, OF matching (`maxim,max77838`), and regulator core. The `regulators` OF subnode and per-rail names are encoded in descriptors.

Risks and test signals: device ID is not validated before registration. The descriptor table is static and assumes all five rails exist. Test LDO versus buck voltage ranges, active-discharge bit polarity, missing regulator child nodes, and regmap max-register coverage.
