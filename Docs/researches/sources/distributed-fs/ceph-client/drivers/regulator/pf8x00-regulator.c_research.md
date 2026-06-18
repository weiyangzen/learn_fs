# sources/distributed-fs/ceph-client/drivers/regulator/pf8x00-regulator.c

Purpose: implements the NXP PF8100/PF8121A/PF8200 regulator driver over I2C. It registers four LDOs, seven buck regulators, and VSNVS with voltage, enable, suspend, and current-limit controls.

Important APIs/types/functions: `struct pf8x00_regulator_data` extends `regulator_desc` with suspend enable/voltage metadata and a cache. `struct pf8x00_chip` holds regmap and device. `swxilim_select()`, `handle_ilim_property()`, and `handle_shift_property()` parse legacy `nxp,ilim-ma` and `nxp,phase-shift` DT properties. `pf8x00_suspend_enable()`, `pf8x00_suspend_disable()`, and `pf8x00_set_suspend_voltage()` implement standby regulator state.

Control flow: probe initializes regmap, validates the PF8x00 family/device ID, then iterates `pf8x00_regs_data` and registers every regulator. Buck OF parsing may adjust current-limit and phase-shift registers during registration. Suspend voltage writes map requested voltages and write standby voltage registers.

State and persistence: global descriptor data is mutated only through per-regulator cache fields and DT callbacks; this is acceptable for one device instance but risky for multiple instances. Suspend voltage caches are volatile memory. Hardware configuration is PMIC register state.

Dependencies and integration: integrates with I2C, regmap, regulator core, and OF regulator parsing. Compatible strings are `nxp,pf8100`, `nxp,pf8121a`, and `nxp,pf8200`.

Risks and test signals: `pf8x00_identify()` can return success on an unknown family after a successful read. Global regulator descriptor mutation can leak between devices. Test all compatibles, invalid IDs, current-limit programming, phase-shift validation, buck/LDO/VSNVS voltage tables, suspend voltage/enable behavior, and multi-instance probe assumptions.
