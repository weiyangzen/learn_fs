# sources/distributed-fs/ceph-client/drivers/regulator/max77541-regulator.c

Purpose: registers the two buck regulators exposed by MAX77540/MAX77541 MFD devices, selecting voltage tables according to the parent chip ID.

Important APIs/types/functions: `max77541_buck_ops` uses pickable linear-range voltage helpers. `MAX77540_BUCK()` and `MAX77541_BUCK()` build descriptors with shared enable register and per-buck VOUT/CFG range registers. `max77541_regulator_probe()` obtains `struct max77541` from the parent and chooses the correct descriptor array.

Control flow: platform probe uses parent driver data to distinguish `MAX77540` from `MAX77541`, then registers `MAX77541_MAX_REGULATORS` descriptors through `devm_regulator_register()`.

State and persistence: no private mutable state is stored in this child driver. The parent MFD owns regmap access, while regulator voltage and enable state reside in PMIC registers.

Dependencies and integration: depends on `linux/mfd/max77541.h`, platform-device MFD instantiation, and regulator core pickable range helpers. Platform IDs are `max77540-regulator` and `max77541-regulator`.

Risks and test signals: incorrect parent chip IDs fail probe. Pickable range tables and selector bitfields must match hardware encoding for both variants. Test buck1/buck2 registration, variant-specific minimum voltages, range selector writes, enable masks, and parent-driver-data absence.
