# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6878.c

## Purpose
This file describes the MT6878 pin controller for the MediaTek Paris core. It maps 196 pins across GPIO plus nine IOCFG regional bases, supplies basic GPIO and mux ranges, rich electrical configuration ranges, per-pin pull-type policy, EINT metadata, explicit EINT pin mapping, advanced drive support, and PM-aware platform-driver registration for `mediatek,mt6878-pinctrl`.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` for 32-bit registers and region-indexed bases. Basic pin control arrays cover mode, direction, DI, and DO. Electrical arrays cover IES, SMT, PU, PD, PUPD, R0, R1, normal drive, advanced drive (`DRV_ADV`), and resistor select (`RSEL`). `mt6878_pull_type` is a 196-entry policy table selecting among `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PU_PD_RSEL_TYPE`, and `MTK_PULL_PUPD_R1R0_TYPE`.

`mt6878_pinctrl_register_base_names` lists ten resource names: `gpio`, `iocfg_bl`, `iocfg_bm`, `iocfg_br`, `iocfg_bl1`, `iocfg_br1`, `iocfg_lm`, `iocfg_lt`, `iocfg_rm`, and `iocfg_rt`. `mt6878_eint_hw` declares one EINT port with port mask `31`, 216 AP EINT lines, 36 debounce counters, and `debounce_time_mt6878`. `mt6878_data` references `mtk_pins_mt6878`, `eint_pins_mt6878`, `nfuncs = 8`, combo bias helpers, the pull-type table, and advanced drive callbacks.

## Control Flow
The file registers `mt6878_pinctrl_driver` during `arch_initcall()`. OF matching on `mediatek,mt6878-pinctrl` provides `mt6878_data` to `mtk_paris_pinctrl_probe()`. The shared Paris implementation then maps all base resources, registers pinctrl/gpio/EINT providers, and uses `mt6878_reg_cals` to translate generic pinmux and pinconf operations into exact MMIO field accesses. Sleep handling is provided through `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`.

## State And Persistence
All local data is const. Hardware state persists in the pin controller registers selected by the range tables. Because MT6878 supports multiple pull models and advanced drive fields, the static `pull_type`, `DRV_ADV`, and `RSEL` ranges directly determine whether a generic bias or drive-strength request writes simple PU/PD bits, PU/PD plus RSEL bits, PUPD/R0/R1 bits, raw drive bits, or advanced drive bits.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6878.h` for pin and EINT-pin descriptors plus debounce metadata, and `pinctrl-paris.h` for the common implementation. It integrates with OF resource naming, pinctrl state selection, gpiolib, EINT/IRQ consumers, and PM sleep pinctrl transitions.

## Risks
MT6878's risk profile is dominated by table complexity. Ten register bases and several electrical models create many opportunities for a pin to target a plausible but wrong offset. The `PINCTRL_PIN_REG_SR` entry maps to `mt6878_pin_dir_range`, which is intentional only if the common core treats SR as unsupported or aliased for this SoC; it deserves scrutiny if slew-rate behavior is expected. The separate `eint_pin` map must remain synchronized with `mt6878_eint_hw` and the pin descriptor header. Advanced drive fields are sparse, so requests on unsupported pins should fail cleanly.

## Test Signals
Use boot/probe logs to verify all ten resources bind, debugfs to confirm 196 pins and eight functions, and targeted pinconf tests for each pull type. Exercise advanced drive on pins listed in `mt6878_pin_drv_adv_range` and verify unsupported pins do not write arbitrary fields. GPIO and mux tests should sample pins from every IOCFG base. EINT tests should cover the explicit EINT pin map, AP EINT numbering, and debounce behavior. Suspend/resume testing should validate the Paris PM integration.
