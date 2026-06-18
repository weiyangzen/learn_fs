# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8365.c

## Purpose
`pinctrl-mt8365.c` supplies legacy MediaTek pinctrl SoC data for MT8365. It defines pin drive groups, per-pin drive register fields, special pull-up/down pins, IES/SMT ranges, a small MT8365-specific pull update helper, EINT hardware layout, and the platform driver that binds the generic legacy `pinctrl-mtk-common.c` implementation to `mediatek,mt8365-pinctrl`.

## Important APIs, Types, And Data
- `mt8365_drv_grp[]` describes three drive-strength encoding classes: 4/8/12/16 mA, 2/4/6/8 mA, and 2 through 16 mA in 2 mA steps.
- `mt8365_pin_drv[]` maps pins 0 through 144 to drive registers around offsets `0x710` through `0x770`, bit positions, and drive group classes.
- `mt8365_spec_pupd[]` lists special PUPD/R1/R0 same-register pins, mostly pins 22-25 and 80-109, used by `mtk_pctrl_spec_pull_set_samereg()`.
- `mt8365_ies_set[]` and `mt8365_smt_set[]` map discontinuous input-enable and Schmitt-trigger ranges to set/clear capable registers around `0x410` through `0x480`.
- `mt8365_set_clr_mode()` updates pull-enable and pull-select with `regmap_update_bits()` on the main registers rather than SET/CLR aliases.
- `mt8365_pinctrl_data` is the `struct mtk_pinctrl_devdata` consumed by `mtk_pctrl_common_probe()`.

## Control Flow
`mtk_pinctrl_init()` registers a platform driver at `arch_initcall`. A device tree node matching `mediatek,mt8365-pinctrl` supplies `mt8365_pinctrl_data` to `mtk_pctrl_common_probe()`. The generic legacy probe builds one group per pin, registers pinctrl, registers GPIO, adds a pin range, and initializes EINT if `ap_num` is nonzero. Runtime pinconf calls select data from this file: generic pull requests first try `spec_pull_set`, then MT8365-specific `mt8365_set_clr_mode()`, while drive strength and IES/SMT are resolved from the static tables.

## State And Persistence
The source declares static immutable tables and one platform driver. Runtime state is in `struct mtk_pinctrl` allocated by `pinctrl-mtk-common.c`; register changes persist in MMIO/syscon hardware. The group config cache stores only the last applied packed pinconf value per single-pin group and is not a full hardware-state mirror.

## Dependencies And Integration Points
The driver uses `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8365.h`, `dt-bindings/pinctrl/mt65xx.h`, regmap, platform-device matching, and the common MediaTek EINT code. The legacy common driver expects a `mediatek,pctl-regmap` phandle or direct regmap path, plus optional interrupt-controller properties. Power management uses `mtk_eint_pm_ops`.

## Risks
`mt8365_set_clr_mode()` intentionally bypasses SET/CLR aliases for pull registers, so offset or bit mistakes can disturb adjacent pull controls. `type1_start` and `type1_end` are both 145; the common helper uses a half-open interval, so no pins select `regmap2`. Drive table coverage ends at pin 144. IES/SMT range entries share bits across many pins, so range mistakes have broad effect.

## Test Signals
Compile the MT8365 pinctrl driver with the legacy common implementation and MT8365 pin header. Boot with `mediatek,mt8365-pinctrl` and confirm common probe, GPIO registration, and EINT initialization. Apply pinctrl states covering generic pulls, special PUPD/R1/R0 pulls, all drive classes, IES/SMT toggles, GPIO direction/get/set, GPIO-to-IRQ, and debounce.
