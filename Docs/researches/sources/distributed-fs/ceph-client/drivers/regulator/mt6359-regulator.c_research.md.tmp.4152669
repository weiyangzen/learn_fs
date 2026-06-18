# sources/distributed-fs/ceph-client/drivers/regulator/mt6359-regulator.c

Purpose: implements the MediaTek MT6359/MT6359P PMIC regulator platform driver. It registers the SoC's buck, fixed LDO, table LDO, and linear LDO rails against the Linux regulator framework using the parent MT6397 MFD regmap.

Important APIs/types/functions: `struct mt6359_regulator_info` extends `regulator_desc` with status, forced-PWM, and low-power-mode registers. Descriptor macros `MT6359_BUCK`, `MT6359_LDO_LINEAR`, `MT6359_LDO`, `MT6359_REG_FIXED`, and `MT6359P_LDO1` populate the MT6359 and MT6359P rail tables. Ops are split across `mt6359_volt_linear_ops`, `mt6359_volt_table_ops`, `mt6359_volt_fixed_ops`, and `mt6359p_vemc_ops`. Special functions include `mt6359_get_status()`, `mt6359_regulator_get_mode()`, `mt6359_regulator_set_mode()`, and MT6359P VEMC selector accessors that unlock TMA and select VEMC_VOSEL_0 or VEMC_VOSEL_1 by hardware trap.

Control flow: probe reads `MT6359P_HWCID` from the parent regmap, chooses the MT6359P descriptor table for chip revisions at or above `MT6359P_CHIP_VER`, then loops through `MT6359_MAX_REGULATOR` and registers each descriptor with `devm_regulator_register()`. Runtime voltage and enable operations are delegated to regulator regmap helpers; buck mode changes write force-PWM and low-power bits, including a 100 us delay when returning from idle to normal.

State and persistence: persistent state is PMIC register state: enable bits, voltage selectors, status bits, force-PWM bits, low-power bits, and TMA-protected VEMC selector registers. Driver state is static descriptor data plus per-rdev `driver_data`; no remove/shutdown restoration is implemented.

Dependencies and integration: depends on the MT6397 MFD core, MT6359/MT6359P register headers, regmap, platform-device binding `mt6359-regulator`, regulator core DT matching under `regulators`, and `mt6359_map_mode()` for DT mode constraints.

Risks and test signals: chip revision detection drives different voltage tables and register addresses, especially VCORE, VGPU11, VRFCK, VEMC, and enable/status registers. `mt6359_regulator_get_mode()` returns raw negative regmap errors through an unsigned mode API. The VEMC TMA unlock path must always re-lock on successful selector writes. Test MT6359 and MT6359P probe, all voltage tables with sparse zero entries, status reads from DA registers, mode transitions FAST/NORMAL/IDLE, invalid DT modes, and VEMC trap 0/1/error cases.
