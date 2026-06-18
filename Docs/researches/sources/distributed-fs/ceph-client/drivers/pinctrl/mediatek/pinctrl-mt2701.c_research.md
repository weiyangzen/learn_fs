# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2701.c

Purpose: Provides MT2701/MT7623 pinctrl SoC data for the older MediaTek common pinctrl framework. It supplies drive groups, per-pin drive mappings, special pull-up/down registers, input-enable/Schmitt ranges, special mux bits, register offsets, and EINT hardware sizing.

Important APIs/types/functions: Main data includes `mt2701_drv_grp`, `mt2701_pin_drv`, `mt2701_spec_pupd`, `mt2701_ies_set`, `mt2701_smt_set`, `mt2701_spec_pinmux`, and `mt2701_pinctrl_data`. Local helpers `mt2701_spec_pinmux_set()` and `mt2701_spec_dir_set()` handle extra mux flag bits and direction register addressing for high pins.

Control flow: The platform driver matches `mediatek,mt2701-pinctrl` or `mediatek,mt7623-pinctrl`, passes `mt2701_pinctrl_data` to `mtk_pctrl_common_probe`, and registers at `arch_initcall`. The common framework uses the tables to service pinmux, GPIO, pinconf, EINT, and PM operations.

State and persistence: This file is static data plus two stateless helper callbacks. Hardware state persists in pinmux, direction, pull, drive, IES/SMT, data, and EINT registers as programmed by the common framework.

Dependencies and integration points: Includes `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt2701.h`, `regmap`, DT binding constants, and MediaTek EINT PM ops. EINT uses `debounce_time_mt2701`, `ap_num=169`, and `db_cnt=16`.

Risks: The per-pin drive and special pull tables are long and hardware-specific; bad offsets or bit positions can damage signal integrity or boot media behavior. `mt2701_spec_pinmux_set()` derives `spec_flag` from mode bit 3 and inverts the register bit when the flag is clear, so mux mode encodings must match hardware expectations. `mt2701_spec_dir_set()` shifts direction registers for pins above 175, which is easy to break with table changes.

Test signals: Build MT2701/MT7623 configs, probe via DT, pinmux for boot media and special pins, pull/drive/IES/SMT get-set, GPIO direction/value for pins above and below 175, EINT mapping/debounce, and suspend/resume through `mtk_eint_pm_ops`.
