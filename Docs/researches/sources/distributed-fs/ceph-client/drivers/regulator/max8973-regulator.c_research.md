# sources/distributed-fs/ceph-client/drivers/regulator/max8973-regulator.c

Purpose: supports MAX8973 and MAX77621 step-down regulators with optional DVS GPIO selection between two VOUT registers, configurable control flags, current limit on MAX77621, and thermal-zone/IRQ support for MAX77621.

Important APIs/types/functions: `struct max8973_chip` owns a mutable descriptor, ops copy, regmap, DVS GPIO, LRU voltage-register state, thermal state, and chip ID. `find_voltage_set_register()` implements two-entry LRU caching. `max8973_init_dcdc()` programs CONTROL1/2 from platform/DT flags. `max8973_thermal_init()` registers a thermal zone and optional threaded IRQ.

Control flow: probe parses platform data or DT, gets optional DVS GPIO, initializes regmap, determines chip ID, reads CHIPID1, builds the descriptor/ops, configures DVS or fixed VSEL behavior, handles enable control differences for MAX8973/MAX77621, initializes hardware control registers, registers the regulator, then initializes thermal support.

State and persistence: LRU arrays and current GPIO/VOUT state track which VOUT register contains which voltage. Hardware stores control flags, voltage selectors, and mode/current-limit settings.

Dependencies and integration: depends on I2C, regmap, GPIO, OF/platform data, regulator core, thermal framework, and IRQ APIs.

Risks and test signals: LRU initialization mixes register addresses and indexes, requiring careful validation. Some final initialization paths log but do not always fail thermal setup. Test DVS and non-DVS paths, external enable GPIO lifecycle, MAX77621 current limit and thermal IRQ, control flag encoding, and multi-step voltage changes.
