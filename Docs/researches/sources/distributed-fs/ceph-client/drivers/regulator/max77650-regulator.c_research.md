# sources/distributed-fs/ceph-client/drivers/regulator/max77650-regulator.c

Purpose: exposes the LDO and three SIMO buck-boost regulators in MAX77650/MAX77651 PMICs, with variant-specific voltage ranges for SBB1/SBB2.

Important APIs/types/functions: `struct max77650_regulator_desc` wraps a regulator descriptor with A/B register addresses. Custom enable ops interpret multi-bit enable fields in the B registers. `max77651_SBB1_regulator_ops` uses pickable linear ranges for the special MAX77651 SBB1 encoding.

Control flow: platform probe inherits the parent OF node if needed, allocates an array of descriptor pointers, obtains the parent regmap, reads the chip ID, picks MAX77650 or MAX77651 SBB descriptors, and registers four regulators.

State and persistence: no persistent private state exists after probe. The parent regmap-backed registers hold enable, voltage, current limit, and active-discharge state.

Dependencies and integration: depends on the MAX77650 MFD core/header, parent regmap, OF regulator nodes, and regulator core current-limit and active-discharge helpers.

Risks and test signals: enable semantics are custom because disabled is a specific multi-bit code, not simply zero. Probe fails on unknown chip IDs. Test MAX77650A/C versus MAX77651A/B descriptor selection, SBB1 pickable range selectors, current-limit table ordering, active discharge bits, and device-tree node inheritance.
