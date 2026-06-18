<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c

Purpose: exposes STM32 embedded analog booster blocks as fixed 3.3 V regulators backed by SYSCFG regmap bits. It supports both STM32H7 single set/clear-by-update behavior and STM32MP1 separate set/clear registers.

Important APIs/types/functions: `stm32h7_booster_desc` uses standard regmap enable/disable/is_enabled helpers on `STM32H7_SYSCFG_PMCR`. `stm32mp1_booster_enable()` writes `STM32MP1_SYSCFG_PMCSETR`; `stm32mp1_booster_disable()` writes `STM32MP1_SYSCFG_PMCCLRR`; `stm32mp1_booster_desc` uses those custom ops. `stm32_booster_probe()` looks up the `st,syscfg` phandle and picks the descriptor from OF match data.

Control flow: probe resolves the syscon regmap, obtains the variant descriptor from `device_get_match_data()`, populates regulator config from the platform node and `of_get_regulator_init_data()`, and registers one regulator. Runtime enable/disable either update the H7 PMCR bit through regmap helpers or write MP1 set/clear registers.

State and persistence: no private mutable state is stored. The booster enable state is in the STM32 SYSCFG register block and is reset according to SoC reset behavior.

Dependencies and integration: depends on OF compatibles `st,stm32h7-booster` and `st,stm32mp1-booster`, a `st,syscfg` phandle, regulator constraints, and the `vdda` supply.

Risks and test signals: MP1 `is_enabled` reads from the set register address, so correctness depends on that register reflecting state rather than being write-only. Test both compatibles, missing syscfg phandle, enable/disable register writes, fixed-voltage reporting, `vdda` supply constraints, and boot-time state readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c -->
