# sources/distributed-fs/ceph-client/drivers/regulator/qcom-rpmh-regulator.c

## Purpose
This driver registers Qualcomm RPMh-managed PMIC regulators. It translates Linux regulator operations for LDO, SMPS, BOB, LVS, and XOB resources into RPMh VRM/TCS commands addressed through the RPMh command database, covering many PMIC families from PM8998 through PM660-era compatibility data.

## Important APIs, Types, and Functions
`struct rpmh_vreg_hw_data` describes regulator class behavior: regulator type, ops table, voltage ranges, mode map, OF mode mapper, and high-performance load threshold. `struct rpmh_vreg` stores the registered descriptor, RPMh address, cached enable/voltage/mode/bypass state, and `qcom,always-wait-for-ack`. Core functions are `rpmh_regulator_send_request()`, `_rpmh_regulator_vrm_set_voltage_sel()`, `rpmh_regulator_set_enable_state()`, `rpmh_regulator_vrm_set_mode_bypass()`, `rpmh_regulator_init_vreg()`, and `rpmh_regulator_probe()`. PMIC-specific arrays built with `RPMH_VREG()` map DT child names to RPMh resource names, hardware data, indices, and supply names.

## Control Flow
Probe reads `qcom,pmic-id`, gets the matched PMIC regulator table, and iterates available child nodes. Each child is matched by node name, converted into an RPMh command DB resource name, resolved with `cmd_db_read_addr()`, configured as a `regulator_desc`, and registered with `devm_regulator_register()`. Runtime enable/disable writes `RPMH_REGULATOR_REG_ENABLE`; voltage writes convert linear-range uV to millivolts and write `RPMH_REGULATOR_REG_VRM_VOLTAGE`; mode and bypass write `RPMH_REGULATOR_REG_VRM_MODE`. Enabling waits for acknowledgment; voltage increases wait, decreases may use async unless `qcom,always-wait-for-ack` is set.

## State and Persistence
The driver has no disk persistence. It caches the last successful voltage selector, enable state, regulator mode, bypass state, RPMh address, and always-ack policy in devm-managed memory. Initial hardware state is mostly unknown (`enabled = -EINVAL`, invalid mode, unrecoverable voltage selector), so voltage may be cached until the first enable/disable request. Hardware programming persists in RPMh/PMIC state until overwritten or reset.

## Dependencies and Integration Points
Integration points are the platform driver framework, OF match data, regulator core, `of_get_regulator_init_data()`, RPMh APIs (`rpmh_write()`, `rpmh_write_async()`), command DB resource lookup, and Qualcomm DT bindings for PMIC regulator child names and `qcom,pmic-id`. The driver exposes standard regulator ops, OF mode mapping, supplies, and constraints to consumers.

## Risks and Test Signals
Risk areas include PMIC table mistakes, command DB resource-name formatting for normal versus `_E` PMIC IDs, async writes racing consumers that expect completion, cached unknown enable/voltage state at boot, and mode-map incompatibilities across PMIC generations. Test signals include successful probe for each compatible, missing-resource failure paths, regulator enable/disable and voltage transitions with RPMh tracing, mode and bypass behavior, fixed-voltage XOB constraints, and DT validation for child names and supplies.
