<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c

Purpose: small platform regulator driver for five Hi6421V530 LDO rails, using table voltages and ECO idle mode support.

Important APIs/types/functions: `struct hi6421v530_regulator_info` stores `regulator_desc` and `mode_mask`; `HI6421V530_LDO()` builds descriptors; `hi6421v530_regulator_ldo_get_mode()` and `_set_mode()` translate normal/idle to masked enable-register bits.

Control flow: probe checks that the parent MFD has `struct hi6421_pmic`, prepares a config with parent device and regmap, then registers each LDO descriptor with devm cleanup. Regulator operations are mostly standard regmap helpers.

State and persistence: no software cache beyond descriptor constants. Enable state, voltage selector, and ECO mode are register state in the PMIC.

Dependencies and integration: depends on `hi6421-pmic` MFD parent data, platform device IDs, OF regulator matching under `regulators`, and the regulator core.

Risks and test signals: mode handlers ignore `regmap_read()`/`regmap_update_bits()` failures and always report success except for invalid mode. Probe is simple, so the main test signals are absent-parent rejection, per-LDO registration, voltage table correctness, mode bit setting, and DT names matching bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c -->
