# sources/distributed-fs/ceph-client/drivers/regulator/axp20x-regulator.c

Purpose: shared regulator driver for many X-Powers AXP PMIC variants, including AXP20x/22x/313A/323/717/803/806/809/813/15060 families, exposing variant-specific DCDC, LDO, switch, RTC, boost, and GPIO-LDO rails.

Important APIs/types/functions: descriptor macros `AXP_DESC*()` generate large variant tables. `axp20x_set_ramp_delay()` handles AXP209 DCDC2/LDO3 slew settings; `axp20x_regulator_enable_regmap()` implements the AXP209 LDO3 soft-start quirk; `axp20x_set_dcdc_freq()` parses and clamps DCDC frequency; `axp20x_set_dcdc_workmode()` writes PWM/auto mode bits; `axp20x_is_polyphase_slave()` suppresses slave rails in multi-phase setups.

Control flow: probe selects a descriptor table from parent `axp20x->variant`, parses top-level regulator properties, then loops through regulators. It skips polyphase slave rails and unsupported AXP813 FLDO3, dynamically patches supply names for internally chained rails, registers each regulator, applies per-regulator `x-powers,dcdc-workmode`, and optionally registers a `drivevbus` regulator after configuring the N_VBUSEN pin.

State and persistence: runtime state is mostly parent `struct axp20x_dev` plus devm-cloned descriptors for dynamic supply names. Hardware register state persists for voltage, enable, workmode, frequency, ramp, and polyphase settings. There is no separate persistent kernel state.

Dependencies and integration: depends on AXP20x MFD register definitions/regmap, OF regulator bindings, regulator core, delay helpers, and platform bus. Variant tables encode hardware quirks and measured deviations from some datasheets.

Risks and test signals: descriptor table drift is the main risk because many variants share registers with subtle differences. `axp20x_regulator_parse_dt()` errors are intentionally ignored by probe. Tests should cover every variant table, AXP209 LDO3 soft-start, DCDC frequency clamping/fixed-frequency rejection, workmode property writes, polyphase skip logic, dynamic supply-name chaining, drive-vbus registration, and AXP813 FLDO3 omission.
