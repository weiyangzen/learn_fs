<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c

Purpose: registers Spreadtrum SC2731 PMIC buck and LDO regulators as simple linear, regmap-backed regulators after unlocking the PMIC regulator write-protect register.

Important APIs/types/functions: `enum sc2731_regulator_id` names three DCDC bucks and fourteen LDOs. `SC2731_REGU_LINEAR()` builds descriptors with inverted enable semantics, voltage selector registers, masks, min/max/step values, and child OF names. `sc2731_regu_linear_ops` uses standard regmap enable, disable, state, list, get, and set voltage helpers. `sc2731_regulator_unlock()` writes `SC2731_WR_UNLOCK_VALUE` to `SC2731_PWR_WR_PROT`.

Control flow: probe obtains the parent regmap with `dev_get_regmap()`, writes the unlock value, then iterates the static descriptor array and registers every regulator. Runtime enable/disable writes PD bits with `enable_is_inverted = true`, so clearing a power-down bit enables the rail.

State and persistence: there is no private mutable software state. All regulator state is in SC2731 PMIC registers. The unlock write is a probe-time hardware side effect and is not represented in software after registration.

Dependencies and integration: depends on a parent MFD/regmap device named by the platform driver `sc27xx-regulator`, regulator core helpers, and DT child nodes matching names such as `BUCK_CPU0`, `LDO_CAMA0`, and `LDO_SRAM`.

Risks and test signals: unlock failure prevents all regulators. Inverted enable fields must match hardware power-down semantics or rails will be reversed. Test with parent regmap absent, write-protect failure, every descriptor's voltage limits, enable/disable polarity, and all child regulator constraints from the SC2731 binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c -->
