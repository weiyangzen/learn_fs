# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2712.c

Purpose: Provides MT2712 pinctrl SoC data for the older MediaTek common framework. It defines special pull-up/down fields, IES/SMT ranges, drive-strength groups, register offsets, and EINT hardware parameters.

Important APIs/types/functions: Core data objects are `mt2712_spec_pupd`, `mt2712_smt_set`, `mt2712_ies_set`, `mt2712_drv_grp`, `mt2712_pin_drv`, and `mt2712_pinctrl_data`. The platform driver matches `mediatek,mt2712-pinctrl` and delegates to `mtk_pctrl_common_probe`.

Control flow: At `arch_initcall`, the platform driver registers. DT match data selects `mt2712_pinctrl_data`; the common framework uses its offsets and callbacks (`mtk_pctrl_spec_pull_set_samereg`, `mtk_pconf_spec_set_ies_smt_range`) to implement mux, GPIO, pinconf, and EINT operations.

State and persistence: The file holds immutable SoC tables. Persistent hardware state is written by the common framework into direction, pull enable/select, data out/in, pinmux, IES/SMT, drive, and EINT registers.

Dependencies and integration points: Depends on `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt2712.h`, regmap, generic pinconf constants, and `mtk_eint_pm_ops`. EINT metadata advertises `ap_num=229`, `db_cnt=40`, eight ports, and the MT2701 debounce timing table.

Risks: Because MT2712 has many range-based IES/SMT entries and special PUPD fields, overlapping or missing ranges can create subtle input and pull behavior errors. Drive group indexes must match `mt2712_drv_grp`. `type1_start`/`type1_end` and register offsets are global common-framework assumptions and should not be changed without auditing the register calculator.

Test signals: Build and DT probe on MT2712, verify all pins enumerate, run mux tests for representative peripherals, validate pull-up/down and drive strength for special and normal pins, test IES/SMT input behavior, EINT edge/level/debounce/wake, and suspend/resume.
