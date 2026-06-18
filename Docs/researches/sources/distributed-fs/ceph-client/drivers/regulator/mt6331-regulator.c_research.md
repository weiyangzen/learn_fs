<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c

## Purpose
Implements MT6331 regulator registration for MT6397-family MFD systems, covering multiple DVFS bucks, fixed regulators, table LDOs, always-on LDOs, and status-register-backed LDO variants.

## Important APIs, Types, And Functions
`struct mt6331_regulator_info` extends descriptors with QI status bits, alternate buck selector registers, mode registers, and optional status registers. Important functions include `mt6331_get_status()`, `mt6331_ldo_set_mode()`, `mt6331_ldo_get_mode()`, `mt6331_set_buck_vosel_reg()`, and `mt6331_regulator_probe()`. Several ops tables distinguish range, table, no-mode, no-QI, always-on, and fixed regulators.

## Control Flow
Probe selects active buck selector registers based on hardware control bits, reads `MT6331_HWCID`, rejects chip ID `0x10` because its voltage tables differ, and registers every descriptor using the parent MFD regmap. LDO mode callbacks write normal/low-power mode fields. Always-on regulators expose voltage operations without enable control. Status for most regulators is QI-based; some special LDOs carry separate status register metadata but the no-QI ops do not currently call `mt6331_get_status()`.

## State And Persistence
The static descriptor table is mutated at probe for active buck VSEL registers. Parent PMIC registers persist enable, status, voltage, and mode state. No dynamic private state beyond regulator device registrations.

## Dependencies And Integration Points
Depends on MT6397 core, MT6331 register and regulator ID headers, platform devices, regmap, and regulator framework. The platform device ID is `mt6331-regulator`.

## Risks And Test Signals
Risks include unsupported E1 chip overvoltage if the ID check regresses, static descriptor mutation across instances, status behavior divergence for `LDO_S` no-QI descriptors, mode masks of zero in no-mode ops, and zero entries in voltage tables. Test by forcing supported and E1 HWCID reads, checking each buck's selected VSEL register, registering all regulators, setting voltage/mode across all LDO categories, and verifying status for QI and status-register rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c -->
