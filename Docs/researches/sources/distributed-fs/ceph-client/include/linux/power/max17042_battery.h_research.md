# sources/distributed-fs/ceph-client/include/linux/power/max17042_battery.h

Purpose: defines register maps, constants, characterization/configuration structures, chip types, and platform data for Maxim MAX17042/MAX17047/MAX17050/MAX17055/MAX77759 fuel-gauge drivers.

Important APIs and types: enums list common MAX17042 registers, MAX17055-specific registers, MAX17047-family registers, MAX77759 registers, and chip types. `struct max17042_reg_data` describes initialization register writes. `struct max17042_config_data` is a packed block of sense-resistor value, ADC calibration, alert/status thresholds, app data, model-gauge configuration, save/restore registers, cell technology, voltage/temperature compensation, and a 48-word characterization table. `struct max17042_platform_data` supplies init/config arrays, POR/current-sense booleans, sense resistor, voltage min/max, and temperature min/max defaults.

Control flow: probe code identifies chip type, loads platform or firmware defaults, optionally performs POR initialization, writes init/config registers, programs model/characterization data, and uses register enums for power_supply property reads and alerts.

State and persistence: static platform/config data is defined here; live gauge state is in the driver and chip registers. Some gauge learned/model data may persist in hardware, and save/restore fields help preserve model-gauge state across resets.

Dependencies and integration points: integrates with power_supply technology constants, I2C/regmap-style register access in the driver, Maxim MFD subdevices, alert IRQ handling, and board/firmware battery characterization data.

Risks and test signals: risks include packed config layout drift, wrong register enum for chip variant, unsafe POR initialization overwriting learned data, sense resistor unit mismatch, invalid characterization tables, and temperature/voltage threshold mistakes. Test chip identification, register reads per variant, POR vs non-POR initialization, model table programming, current-sense scaling, alert thresholds, suspend/resume, and power_supply property accuracy.
