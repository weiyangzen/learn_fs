<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c

Purpose: provides regulator support for the SpacemiT P1 PMIC, registering six bucks, four analog LDOs, and seven digital LDOs using the parent PMIC regmap.

Important APIs/types/functions: `enum p1_regulator_id` names all rails. `p1_regulator_ops` uses linear-range voltage selection, regmap enable/disable, enable state, and voltage transition timing helpers. `p1_buck_ranges[]` covers two buck voltage segments with selector 255 reserved for sleep disable. `p1_ldo_ranges[]` starts at selector 11, with selector 0 reserved for suspend. `P1_REG_DESC()` and wrapper macros derive register offsets, selector masks, supply names, and OF names.

Control flow: the platform driver `spacemit-p1-regulator` is probed by the parent PMIC. Probe sets `config.dev` to the parent so the regulator core can use the parent regmap, then registers each static descriptor. Runtime operations are standard regmap helper callbacks.

State and persistence: this file stores no private state. Voltage selectors and enables live in PMIC registers. Sleep/suspend-reserved selector values are documented by the ranges but no custom suspend callback is implemented here.

Dependencies and integration: depends on the parent PMIC platform device/regmap, OF child nodes named `buck1`-`buck6`, `aldo1`-`aldo4`, and `dldo1`-`dldo7`, and regulator consumers for `vin#`, `aldoin`, `dldoin1`, and `dldoin2` supplies.

Risks and test signals: register offset math is macro-driven and should be checked against the PMIC datasheet. Buck `n_voltages = 255` intentionally excludes selector 255; LDO ranges expose 128 selectors while valid output starts at selector 11. Test all descriptors for vsel/en register addresses, voltage list/map around range boundaries, parent regmap lookup, and board constraints that avoid sleep/suspend selector misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c -->
