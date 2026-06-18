<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c

## Purpose
Provides the MT6323 platform regulator subdriver for the MT6397-family MFD core, registering bucks, table LDOs, and fixed LDOs.

## Important APIs, Types, And Functions
`struct mt6323_regulator_info` stores descriptor data plus QI status, alternate voltage selector registers, voltage-control register metadata, and LDO mode registers. Key functions are `mt6323_get_status()`, `mt6323_ldo_set_mode()`, `mt6323_ldo_get_mode()`, `mt6323_set_buck_vosel_reg()`, and `mt6323_regulator_probe()`.

## Control Flow
Probe receives the parent `mt6397_chip`, checks buck control registers to decide whether each buck should use normal `vosel` or active `voselon` register, reads and logs chip ID, then registers all MT6323 regulators. Buck regulators use linear ranges. LDOs use voltage tables or fixed voltages. LDO mode callbacks map NORMAL/STANDBY to one-bit low-power controls when the descriptor provides a mode register.

## State And Persistence
The static regulator table is mutated at probe when a buck's active selector register is selected. The parent regmap stores all hardware state. No additional private state is allocated per driver instance beyond passing each table entry as driver data.

## Dependencies And Integration Points
Depends on the MT6397 MFD parent, MT6323 register and regulator ID headers, platform driver infrastructure, regmap, and regulator core. The driver uses the parent device's regmap and platform ID `mt6323-regulator`.

## Risks And Test Signals
Risks include static descriptor mutation, incorrect buck control register selection, LDOs with no mode register returning errors if mode callbacks are invoked, and voltage table holes represented as zero. Test by probing under the parent MFD, validating selected `vsel_reg` for each buck, registering all regulators, checking QI-based status, setting LDO standby/normal modes where supported, and exercising voltage mapping for table holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c -->
