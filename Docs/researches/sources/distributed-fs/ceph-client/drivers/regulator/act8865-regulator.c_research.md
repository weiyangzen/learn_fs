# sources/distributed-fs/ceph-client/drivers/regulator/act8865-regulator.c

Purpose: supports Active-Semi ACT8600, ACT8846, and ACT8865 PMIC regulators over I2C, with optional ACT8600 charger status reporting and system-power-off integration for ACT8846/ACT8865.

Important APIs/types/functions: `struct act8865` stores regmap and shutdown register data. `act8865_set_mode()`, `act8865_get_mode()`, and suspend helpers program ACT8865 control/suspend registers; descriptor arrays `act8600_regulators[]`, `act8846_regulators[]`, `act8865_regulators[]`, and `act8865_alt_regulators[]` define rails. `act8600_charger_probe()` registers a `power_supply`.

Control flow: probe identifies the chip from OF or I2C ID, chooses descriptor and regmap configuration tables, optionally installs `pm_power_off`, registers all regulators, adds the ACT8600 charger device if applicable, stores client data, and unlocks ACT8865 expert registers. Regulator ops use generic regmap helpers for voltage, enable, pull-down, and linear-range mapping.

State and persistence: device state is devm-managed `struct act8865`, a global `act8865_i2c_client` for power-off, and hardware registers. `active-semi,vsel-high` selects the alternate ACT8865 DCDC VSET bank at probe only. Suspend settings and mode bits persist in PMIC registers until changed.

Dependencies and integration: integrates I2C, regmap access tables, OF bindings, regulator core, power-supply core, and global power-off handling. Platform-data fallback still exists for non-OF regulator init data.

Risks and test signals: global `pm_power_off` ownership can conflict with another power controller. ACT8600 has restricted readable/writable/volatile register tables, so bad ranges surface as regmap failures. Test ACT8600/8846/8865 descriptor counts, VSET-high selection, charger status decoding, suspend-enable writes, power-off register writes, and probe deferral from power-supply registration.
