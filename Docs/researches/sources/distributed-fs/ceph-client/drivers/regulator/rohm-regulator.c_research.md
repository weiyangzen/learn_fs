# sources/distributed-fs/ceph-client/drivers/regulator/rohm-regulator.c

Purpose: supplies shared helper routines for ROHM PMIC regulator drivers rather than registering regulators itself. It programs device-tree-defined DVS voltage levels and provides a restricted voltage setter for rails that must be disabled before voltage changes.

Important APIs/types/functions: `rohm_regulator_set_dvs_levels()` iterates a `struct rohm_dvs_config` level map and applies properties such as `rohm,dvs-run-voltage`, `rohm,dvs-idle-voltage`, and suspend/deep-sleep variants. `set_dvs_level()` resolves a requested microvolt value against the descriptor's linear or linear-range voltage table, writes the selector, and optionally writes an enable mask. `rohm_regulator_set_voltage_sel_restricted()` returns `-EBUSY` when the target rail is enabled.

Control flow: callers pass a DVS config, OF node, descriptor, and regmap. For each enabled DVS level, the helper reads the DT property, treats zero as disable when an on-mask exists, maps the exact voltage to a selector, writes the selector register, then enables that DVS state if needed.

State and persistence: this file owns no state. It mutates PMIC registers supplied by caller drivers. DVS settings persist as PMIC register state until reset or reprogramming.

Dependencies and integration: exported symbols are consumed by ROHM PMIC regulator drivers sharing `include/linux/mfd/rohm-generic.h` DVS conventions. It relies on regulator descriptor voltage-list helpers and regmap.

Risks and test signals: exact-voltage matching rejects unsupported but nearby voltages, and pickable range selectors are explicitly unsupported. A property value of zero has special disable semantics. Tests should exercise absent properties, invalid properties, supported and unsupported voltages, enable-only DVS levels with no voltage mask, and enabled-rail restricted voltage writes.
