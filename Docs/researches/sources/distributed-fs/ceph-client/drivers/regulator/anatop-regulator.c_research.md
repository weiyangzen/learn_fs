# sources/distributed-fs/ceph-client/drivers/regulator/anatop-regulator.c

Purpose: generic Freescale/NXP ANATOP syscon regulator driver, mainly for i.MX analog LDO-style regulators described entirely by DT bit offsets and voltage ranges.

Important APIs/types/functions: `struct anatop_regulator` stores dynamic descriptor, delay register geometry, cached selector, and bypass flag. Core ops implement enable/disable via selector values, bypass via FET full-on selector, cached set/get while disabled or bypassed, and `anatop_regmap_set_voltage_time_sel()` computes ramp-up delay from ANATOP delay bits.

Control flow: probe reads `regulator-name`, regulator init data, parent syscon regmap, voltage control offset/bit geometry, min selector, min/max voltage, and optional delay/enable fields. Core regulators with delay bits use `anatop_core_rops`; simpler regulators use `anatop_rops`, patched at runtime if an enable bit exists. It then registers one regulator device.

State and persistence: hardware selector zero means power gate and selector `0x1f` means full FET bypass for core regulators. The driver caches the intended voltage selector while disabled or bypassed. Register state persists in the syscon until changed.

Dependencies and integration: depends on OF-only platform data, parent syscon regmap, regulator core, and board-specific DT properties such as `anatop-reg-offset` and `anatop-vol-bit-width`.

Risks and test signals: `anatop_rops` is a mutable global ops table; once any instance adds enable ops, later simple instances share them. DT geometry errors can silently create wrong masks or invalid voltage counts. Tests should cover vddpu/vddpcie default selector fallbacks, bypass transitions, disabled voltage cache, missing required DT properties, ramp-delay calculation, and multi-instance behavior with mixed enable-bit support.
