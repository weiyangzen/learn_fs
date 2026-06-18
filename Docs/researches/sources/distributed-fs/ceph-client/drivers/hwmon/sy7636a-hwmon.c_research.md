
# sources/distributed-fs/ceph-client/drivers/hwmon/sy7636a-hwmon.c

Purpose: platform hwmon child for the SY7636A MFD, exposing the PMIC thermistor readout as a temperature channel.

Important APIs, types, and functions: `sy7636a_read()` reads `SY7636A_REG_TERMISTOR_READOUT` through the parent regmap and scales the register value by 1000 to hwmon millidegrees. `sy7636a_is_visible()` only exposes `hwmon_temp_input`. `sy7636a_sensor_probe()` obtains the parent regmap, enables the `vcom` regulator, and registers `sy7636a_temperature`.

Control flow, state, and persistence: probe defers if no parent regmap exists, requires regulator enable success, then registers hwmon. No cache or writable state is kept by this driver.

Dependencies and integration points: integrates with the `sy7636a` MFD header, parent regmap, regulator framework, platform alias `sy7636a-temperature`, and hwmon thermal-zone flag.

Risks and test signals: the sensor depends on `vcom` being enabled, so regulator errors block hwmon registration. Scaling assumes the MFD register already reports degrees C units. Test probe deferral, regulator failure, regmap read errors, normal conversion, and platform alias autoload.
