# sources/distributed-fs/ceph-client/drivers/regulator/rt5759-regulator.c

Purpose: implements the Richtek RT5759/RT5759A single buck regulator with voltage selection, enable, active discharge, mode, ramp delay, error flags, configurable OCP/OTP thresholds, and optional RT5759A watchdog input.

Important APIs/types/functions: `struct rt5759_priv` stores chip type, regmap, and descriptor. `rt5759_regulator_register()` fills descriptor fields and adjusts `uV_step` for RT5759A. `rt5759_manufacturer_check()` verifies vendor ID. `rt5759_set_ocp()` and `rt5759_set_otp()` map regulator protection requests to register levels.

Control flow: probe allocates state, obtains chip type from OF match data, initializes regmap with chip-type-aware accessible registers, checks manufacturer ID, applies the RT5759A watchdog property if applicable, then registers the buck regulator. Runtime mode and protection writes update DCDC control/status/set registers; status reads report overtemperature and undervoltage errors.

State and persistence: chip type and descriptor are driver state. Hardware registers store voltage, enable, discharge, ramp, mode, protection thresholds, watchdog enable, and status.

Dependencies and integration: depends on I2C, OF match data, regmap readable/writeable callbacks, regulator protection APIs, and OF regulator init data.

Risks and test signals: `rt5759_set_mode()` writes `RT5759_REG_STATUS` while `get_mode()` reads `RT5759_REG_DCDCCTRL`, a potential register mismatch to verify against datasheet. Protection setters ignore non-protection severities by returning success. Tests should cover both chip types, vendor mismatch, watchdog property access only on RT5759A, voltage step differences, ramp table, mode set/get consistency, and OCP/OTP threshold rounding.
