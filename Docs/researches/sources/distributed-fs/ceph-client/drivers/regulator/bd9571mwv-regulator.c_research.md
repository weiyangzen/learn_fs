# sources/distributed-fs/ceph-client/drivers/regulator/bd9571mwv-regulator.c

Purpose: This driver registers voltage monitor/control entries for ROHM BD9571MWV-M and BD9574MWF-M PMICs. BD9571 exposes VD09, VD18, VD25, VD33, and DVFS regulators or monitors; BD9574 exposes DVFS only. The file also manages optional DDR backup power behavior across suspend/resume and through a sysfs `backup_mode` attribute.

Important APIs, types, and functions: `struct bd9571mwv_reg` stores the regmap and backup-mode configuration derived from device tree. `BD9571MWV_REG()` builds linear regulator descriptors. `bd9571mwv_avs_get_moni_state()` reads the AVS monitor state used to select the active VD09 VID register. `bd9571mwv_avs_set_voltage_sel_regmap()` and `_get_voltage_sel_regmap()` operate on the AVS VID register selected by monitor state. `bd9571mwv_reg_set_voltage_sel_regmap()` writes DVFS set VID. `backup_mode_show()` and `backup_mode_store()` expose backup mode when sleep PM is enabled.

Control flow: Probe allocates private state, gets the parent regmap, sets the child OF node from the parent, registers all applicable descriptors, and then reads device-tree properties `rohm,ddr-backup-power`, `rohm,rstbmode-level`, and `rohm,rstbmode-pulse`. It rejects invalid backup-power bitfields and mutually exclusive reset-mode properties. If backup power is configured and `CONFIG_PM_SLEEP` is enabled, it creates `backup_mode`; pulse mode enables backup mode by default, while level mode expects user control.

State and persistence behavior: Voltage selector state is stored in PMIC VID registers. Backup mode state is partially driver-held (`bkup_mode_enabled`, saved mode byte) and partially persistent in `BD9571MWV_BKUP_MODE_CNT`. Suspend saves current backup mode and, in pulse mode, writes keep-on bits before sleep. Resume restores the saved value. In level mode the sysfs store path writes keep-on bits immediately when toggled.

Dependencies and integration points: The driver depends on `rohm-generic` chip IDs, `bd9571mwv.h` registers, regmap, regulator core, platform IDs, OF properties, and optional PM sleep. It uses devm regulator registration and platform driver remove only to remove sysfs when PM sleep support compiled it in.

Risks: The AVS VD09 path chooses a VID register based on monitor state at access time, so a state transition between get/set assumptions can surprise callers. Backup mode sysfs exists only under PM sleep builds and only when a nonzero keep-on mask is configured. `bdreg->regmap` is not explicitly checked for NULL before use. Backup mode property validation only checks bit mask validity, not board-level safety.

Test signals: Cover BD9571 versus BD9574 registration filtering, AVS monitor-selected register reads/writes, DVFS set VID writes, invalid backup-power values, conflicting reset-mode DT properties, sysfs backup mode toggling in level mode, suspend/resume save/restore in pulse mode, and no-backup-power paths.
