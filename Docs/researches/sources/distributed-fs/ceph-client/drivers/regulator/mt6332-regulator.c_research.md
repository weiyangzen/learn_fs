<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c

## Purpose
Provides MT6332 regulator support for MT6397-family MFD systems, including bucks, boost, linear LDO, table LDOs, always-on LDO, and fixed regulators.

## Important APIs, Types, And Functions
`struct mt6332_regulator_info` mirrors MT6331-style metadata: QI bits, alternate selector registers, mode registers, and optional status registers. Key callbacks are `mt6332_get_status()`, `mt6332_ldo_set_mode()`, `mt6332_ldo_get_mode()`, `mt6332_set_buck_vosel_reg()`, and `mt6332_regulator_probe()`. Ops tables cover buck linear ranges, LDO linear ranges, voltage tables, always-on tables, and fixed regulators.

## Control Flow
Probe selects each buck/LDO linear regulator's active voltage selector register based on control bits, reads and masks `MT6332_HWCID`, rejects chip ID `0x10` for unsupported E1 voltage tables, and registers every descriptor. Status uses QI when present and falls back to descriptor status register/mask otherwise. LDO mode callbacks map NORMAL/STANDBY to low-power mode bits.

## State And Persistence
The static descriptor table can be modified at probe by switching `desc.vsel_reg` to `vselon_reg`. Hardware state is held in parent PMIC registers. No extra dynamic per-device state is kept.

## Dependencies And Integration Points
Depends on MT6397 MFD core, MT6332 register and regulator ID headers, platform driver matching, regmap, and regulator framework. Platform ID is `mt6332-regulator`.

## Risks And Test Signals
Risks include E1 voltage-table incompatibility, active selector register selection, mixed QI/status status paths, mode ops on descriptors with invalid masks, and boost/buck voltage range limits. Test by HWCID gating, register selection checks, voltage sweeps for buck/boost/LDO ranges, mode toggles on mode-capable LDOs, and status readback for fixed regulators using `MT6332_EN_STATUS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c -->
