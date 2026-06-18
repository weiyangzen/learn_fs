# sources/distributed-fs/ceph-client/drivers/regulator/qcom-pm8008-regulator.c

Purpose: implements the Qualcomm PM8008 PMIC regulator child driver. It registers seven LDO regulators using a parent secondary regmap, with NLDO/PLDO voltage ranges, enable control, dropout metadata, and ramp delay derived from hardware step-rate bits.

Important APIs/types/functions: `struct pm8008_regulator` stores the parent regmap, per-instance descriptor, and base offset. `struct pm8008_regulator_data` defines each LDO name, supply name, base, dropout, and voltage range. `pm8008_regulator_set_voltage_sel()` converts selected microvolts to millivolts and writes a little-endian 16-bit value via `regmap_bulk_write()`. `pm8008_regulator_get_voltage_sel()` bulk reads the 16-bit millivolt register and maps it back to a selector.

Control flow: probe gets the parent `"secondary"` regmap, iterates the seven static LDO entries, allocates a regulator object and descriptor, fills descriptor names, OF match, supply, voltage range, selector count, step/dropout, reads stepper control to compute `ramp_delay`, sets enable register/mask, and registers each regulator.

State and persistence: descriptors and state are per-regulator devm allocations. Voltage and enable settings are PMIC register state. No software voltage cache is used.

Dependencies and integration: depends on platform bus, parent MFD/regmap exposing `"secondary"`, regulator core, OF regulator child nodes under `regulators`, and little-endian register encoding.

Risks and test signals: config uses `config.dev = dev->parent` while allocation and registration use the child device, so sysfs/regulator parentage should be checked. Voltage writes round up to millivolts; selector mapping on read should tolerate hardware values not exactly on a linear step. Test all seven LDOs, missing secondary regmap, ramp delay values, LE bulk read/write behavior, dropout constraints, and enable bits.
