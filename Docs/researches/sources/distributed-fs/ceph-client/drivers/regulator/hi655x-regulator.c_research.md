<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c

Purpose: HiSilicon Hi655x LDO regulator driver registering selected LDO rails from an MFD parent.

Important APIs/types/functions: `struct hi655x_regulator` extends `regulator_desc` with separate disable and status registers. `hi655x_is_enabled()` reads status, `hi655x_disable()` writes a disable latch, and descriptor macros define table and linear LDO variants.

Control flow: probe retrieves `struct hi655x_pmic`, fills a shared config with parent regmap, sets `driver_data` to each static regulator record, and registers all descriptors. Enables and voltage selector operations use standard regmap helpers; disable and status use chip-specific registers.

State and persistence: no mutable driver state beyond static descriptor records. Register writes persist according to PMIC state; disable is not a normal masked clear but a write to a disable register.

Dependencies and integration: depends on `linux/mfd/hi655x-pmic.h`, platform MFD enumeration, OF regulator matching, and regulator core table/linear helpers.

Risks and test signals: `hi655x_is_enabled()` ignores read failures and returns a masked value as a boolean-ish integer. Several enum IDs are not implemented in the descriptor array, so platform data and bindings must match supported rails. Tests should cover enable/status/disable register separation, DT naming, and invalid parent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c -->
