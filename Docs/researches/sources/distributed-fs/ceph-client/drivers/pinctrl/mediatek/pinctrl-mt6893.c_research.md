# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6893.c

## Purpose
This file provides the MT6893 SoC data table for the MediaTek Paris pinctrl core. It describes 220 pins across ten named register bases, including mux/GPIO control, Schmitt/input-enable, pull-up/down, mixed advanced pull models, normal and advanced drive strength, RSEL fields, EINT hardware, and PM-aware platform-driver registration.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` expand to `PIN_FIELD_CALC()` for 32-bit registers with base indices. Basic field arrays are `mt6893_pin_mode_range`, `mt6893_pin_dir_range`, `mt6893_pin_di_range`, and `mt6893_pin_do_range`. Electrical arrays include `mt6893_pin_smt_range`, `mt6893_pin_ies_range`, `mt6893_pin_pu_range`, `mt6893_pin_pd_range`, `mt6893_pin_drv_range`, `mt6893_pin_pupd_range`, `mt6893_pin_r0_range`, `mt6893_pin_r1_range`, `mt6893_pin_drv_adv_range`, and `mt6893_pin_rsel_range`.

`mt6893_pull_type` is a 220-entry per-pin selector for `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PUPD_R1R0_TYPE`, and `MTK_PULL_PU_PD_RSEL_TYPE`. `mt6893_pinctrl_register_base_name` names the resources as `base`, `rm`, `bm`, `bl`, `br`, `lm`, `lb`, `rt`, `lt`, and `tl`. `mt6893_reg_cals` maps all supported register classes, including `DRV_ADV` and `RSEL`. `mt6893_eint_hw` describes seven EINT ports, 224 AP EINT lines, 32 debounce counters, and `debounce_time_mt6765`. `mt6893_data` selects rev1 drive callbacks for normal drive, raw advanced drive callbacks for advanced drive, combo bias helpers, `nfuncs = 8`, and the pull-type table.

## Control Flow
`arch_initcall(mt6893_pinctrl_init)` registers the platform driver. The OF match table binds `mediatek,mt6893-pinctrl` and supplies `mt6893_data` to `mtk_paris_pinctrl_probe()`. The shared probe maps the named resources, registers pinctrl/gpio/EINT providers, and uses `mt6893_reg_cals` for subsequent pinmux and pinconf operations. PM sleep callbacks are enabled through `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`.

## State And Persistence
The file has no mutable state. It persists behavior by defining the static mapping from pin numbers to hardware fields. Runtime changes are MMIO register writes made by the Paris core for mux mode, GPIO state, bias, Schmitt, input enable, drive strength, advanced drive, RSEL, and EINT debounce/trigger state.

## Dependencies And Integration Points
The driver depends on `pinctrl-mtk-mt6893.h` for pin descriptors and debounce data, `pinctrl-paris.h` for probe and callbacks, OF platform binding, gpiolib, generic pinctrl/pinconf, MediaTek EINT, and PM sleep integration. Device tree must expose register resources with names matching `mt6893_pinctrl_register_base_name`.

## Risks
MT6893 has a large and irregular field map. Pull behavior is especially sensitive because different pins use PU/PD, PUPD/R0/R1, or PU/PD/RSEL models. The normal drive callbacks use rev1 helpers while advanced drive uses raw helpers, so field widths and value encoding must match the common helper's expectations. `PINCTRL_PIN_REG_SR` maps to the direction range, which should be reviewed if clients require explicit slew-rate control. The EINT debounce table reuses `debounce_time_mt6765`; this is probably intentional only if MT6893 shares timing values.

## Test Signals
Probe should succeed with all ten named resources. Debugfs should show 220 pins/groups and eight functions. Pinmux tests should sample pins in each region. Pinconf tests should cover each pull type, normal rev1 drive, raw advanced drive, Schmitt, IES, and unsupported-field behavior. EINT tests should cover several ports and debounce counters. Suspend/resume tests should confirm state restoration through the Paris PM ops.
