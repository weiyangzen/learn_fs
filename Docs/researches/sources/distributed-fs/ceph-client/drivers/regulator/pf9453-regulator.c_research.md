# sources/distributed-fs/ceph-client/drivers/regulator/pf9453-regulator.c

Purpose: implements the NXP PF9453 PMIC regulator driver over I2C. It registers four buck regulators, two LDOs, and LDOSNVS, supports protected-register writes, DVS properties for BUCK2, IRQ logging, watchdog reset configuration, and optional SD_VSEL GPIO control.

Important APIs/types/functions: `struct pf9453` stores device, regmap, IRQ, and optional `sd-vsel` GPIO. `struct pf9453_regulator_desc` carries a `regulator_desc` plus DVS register metadata. `is_reg_protect()` identifies voltage registers that require lock/unlock sequencing. `pf9453_pmic_write()` performs masked writes and unlocks protected registers with `PF9453_UNLOCK_KEY`. Custom enable, disable, voltage-select, and ramp-delay ops wrap regulator helpers to use protected writes.

Control flow: probe requires an IRQ, initializes regmap, validates device ID high nibble, registers regulators from OF match data until the sentinel, requests a shared threaded IRQ, unmasks selected interrupts, configures WDOG_B warm/cold reset behavior from DT, and drives optional `sd-vsel` high so LDO1 uses `LDO1OUT_H`.

State and persistence: no per-regulator runtime cache except hardware registers. DVS settings and reset behavior are written to PMIC registers during probe. GPIO lifetime is devm-managed.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, OF, and regulator core. Compatible is `nxp,pf9453`.

Risks and test signals: `pf9453_pmic_write()` silently skips writes when `reg >= PF9453_MAX_REG`; call sites should never pass bad registers. DVS parsing loops standby and deep-standby over the same property/register, causing duplicate writes. IRQ handling logs but does not notify regulator consumers. Test protected writes, DVS properties, WDOG_B property, SD_VSEL behavior, IRQ status, and BUCK2 ramp/voltage ops.
