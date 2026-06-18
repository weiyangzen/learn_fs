<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c

## Purpose
Implements MT6357 regulator registration for the MT6397-family PMIC core, covering bucks, selectable LDOs, SRAM LDOs with monitor selectors, and fixed LDOs.

## Important APIs, Types, And Functions
`struct mt6357_regulator_info` wraps descriptors with DA voltage monitor register and mask. Descriptor macros define buck, table LDO, linear SRAM LDO, and fixed regulator entries. The main custom callback is `mt6357_get_buck_voltage_sel()`, shared by buck/range/fixed ops where DA monitor readback is needed. Probe is `mt6357_regulator_probe()`.

## Control Flow
Probe inherits the parent OF node, iterates the static regulator table, passes each entry as driver data, and registers all regulators against the parent regmap. Voltage set uses normal descriptor VSEL registers, while get-voltage for bucks and linear SRAM LDOs reads DA debug registers to report actual hardware-selected values.

## State And Persistence
The driver uses a static descriptor table and no per-device allocation. Hardware register values and parent regmap hold regulator state. No static table mutation is performed.

## Dependencies And Integration Points
Depends on MT6397 core, MT6357 register and regulator headers, platform devices, regmap, OF regulator matching, and regulator core. Platform ID is `mt6357-regulator`.

## Risks And Test Signals
Risks include voltage table holes, DA monitor mask/shift mistakes, fixed regulators exposing calibrated selector behavior inconsistently, and assuming parent regmap readiness. Test by registering all MT6357 regulators, reading DA selectors after voltage changes, checking fixed LDO enables, validating table voltage mapping with zero entries, and confirming child regulator DT names match descriptor `of_match` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c -->
