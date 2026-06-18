# sources/distributed-fs/ceph-client/drivers/i2c/muxes/Kconfig

Purpose: Kconfig menu for I2C mux, gate, arbitrator, and demux drivers under `drivers/i2c/muxes`. The whole menu depends on `I2C_MUX`.

Important symbols: entries include `I2C_ARB_GPIO_CHALLENGE`, `I2C_MUX_GPIO`, `I2C_MUX_GPMUX`, `I2C_MUX_LTC4306`, `I2C_MUX_PCA9541`, `I2C_MUX_PCA954x`, `I2C_MUX_PINCTRL`, `I2C_MUX_REG`, `I2C_DEMUX_PINCTRL`, `I2C_MUX_MLXCPLD`, and `I2C_MUX_MULE`.

Control flow: build configuration selects which mux drivers compile as built-in or modules. Several symbols enforce subsystem dependencies such as `GPIOLIB`, `OF`, `PINCTRL`, `HAS_IOMEM`, `SENSORS_AMC6821`, `MULTIPLEXER`, and `REGMAP_I2C`.

State and persistence: no runtime state; it controls kernel build state and module availability.

Dependencies and integration: integrates with the I2C mux core and each driver source listed in the corresponding Makefile. Help text documents expected module names.

Risks: dependency mismatches can create build failures or unusable runtime configs. `I2C_MUX_MULE` depends on a specific hwmon sensor driver because the Mule parent function supplies the regmap. `I2C_DEMUX_PINCTRL` selects `OF_DYNAMIC`, reflecting runtime OF changeset requirements.

Test signals: `olddefconfig`, allmodconfig, compile-test combinations for GPIO/OF/PINCTRL/MUX, and verifying module names match Makefile objects.
