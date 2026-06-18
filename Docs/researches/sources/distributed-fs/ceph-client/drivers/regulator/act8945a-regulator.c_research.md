# sources/distributed-fs/ceph-client/drivers/regulator/act8945a-regulator.c

Purpose: platform child regulator driver for the Active-Semi ACT8945A PMIC, exposing three DCDC and four LDO voltage rails behind a parent MFD regmap.

Important APIs/types/functions: `struct act8945a_pmic` keeps the parent regmap and cached `op_mode[]`. `act8945a_set_suspend_state()`, `set_suspend_enable()`, `set_suspend_disable()`, `set_mode()`, and `get_mode()` implement regulator-specific control. `ACT89xx_REG()` builds the normal and alternate descriptor tables.

Control flow: probe allocates state, fetches the parent regmap, chooses normal or `active-semi,vsel-high` DCDC VSET registers, mirrors the parent OF node onto the platform child, registers all regulators, stores drvdata, and writes `ACT8945A_SYS_UNLK_REGS` to unlock expert registers. PM suspend writes `ACT8945A_SYS_CTRL` to request suspend on the next PWRHLD transition; shutdown writes the same register to request full shutdown.

State and persistence: `op_mode[]` is an in-memory cache updated only through this driver’s `set_mode()` path; `get_mode()` does not reread hardware. Voltage, enable, suspend, and shutdown state are PMIC registers. No persistent kernel storage exists.

Dependencies and integration: depends on parent MFD regmap, platform bus, regulator core, OF regulator descriptors, and PM hooks. It assumes the parent node contains regulator child definitions.

Risks and test signals: cached mode can be stale if firmware, bootloader, or another path changes mode bits. Suspend/shutdown programming is board-sensitive because it acts on PWRHLD transitions. Tests should cover both VSET banks, mode cache behavior, suspend register writes, shutdown path, parent-regmap absence, and regulator registration failure.
