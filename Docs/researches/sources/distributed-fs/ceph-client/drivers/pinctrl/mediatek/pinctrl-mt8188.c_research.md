# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8188.c

## Purpose

This file is the MT8188 Paris pinctrl data driver. It describes 178 pins across five named IO configuration bases and supplies register calculators for mux, GPIO, IES, SMT, transmit/receive select, PU/PD, PUPD/R0/R1, drive, advanced drive, RSEL resistance selection, EINT, and module metadata.

## Important APIs, Types, And Functions

The main local macros are `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()`. Major arrays are `mt8188_pin_mode_range`, `mt8188_pin_dir_range`, `mt8188_pin_di_range`, `mt8188_pin_do_range`, `mt8188_pin_smt_range`, `mt8188_pin_ies_range`, `mt8188_pin_tdsel_range`, `mt8188_pin_rdsel_range`, `mt8188_pin_pupd_range`, `mt8188_pin_r0_range`, `mt8188_pin_r1_range`, `mt8188_pin_pu_range`, `mt8188_pin_pd_range`, `mt8188_pin_drv_range`, `mt8188_pin_drv_adv_range`, `mt8188_pin_rsel_range`, `mt8188_pin_rsel_val_range`, and `mt8188_pull_type`.

`mt8188_reg_cals` wires those arrays to the Paris register enum, notably including `PINCTRL_PIN_REG_TDSEL` and `PINCTRL_PIN_REG_RDSEL` in addition to pull and drive registers. `mt8188_data` supplies `struct mtk_pin_soc` fields, pin descriptors, five base names, pull type and RSEL lookup data, rev1 drive callbacks, raw advanced-drive callbacks, and combo bias callbacks.

## Control Flow

At `arch_initcall`, the platform driver is registered. OF matching on `mediatek,mt8188-pinctrl` passes `mt8188_data` to `mtk_paris_pinctrl_probe`. The probe maps `iocfg0`, `iocfg_rm`, `iocfg_lt`, `iocfg_lm`, and `iocfg_rt`, builds pin state, registers and enables the pinctrl device, initializes EINT if possible, and adds the GPIO chip.

Runtime pin operations are handled by the Paris core. Basic mux and GPIO operations use contiguous mode/dir/DI/DO ranges. Pinconf uses IES/SMT tables, TDSEL/RDSEL tables for timing-related custom configs, PU/PD tables for most pins, PUPD/R0/R1 tables for R1/R0-style pins, and RSEL/advanced-drive tables for selected high-speed pins.

## State And Persistence

This file contributes static const SoC metadata only. Runtime state is held by the Paris core and hardware registers. The `pull_type` table is per-pin policy state compiled into the driver; it determines how generic bias operations select register families. Hardware register settings persist until reset, power-domain loss, suspend restoration behavior, or later pinctrl calls. The driver uses `mtk_paris_pinctrl_pm_ops` and declares `MODULE_DESCRIPTION`.

## Dependencies And Integration Points

Dependencies include `linux/module.h`, `pinctrl-mtk-mt8188.h`, `pinctrl-paris.h`, common v2 pinctrl definitions, Linux OF/platform resource mapping, pinctrl/GPIO, and EINT. EINT metadata advertises seven ports, 225 AP interrupt numbers, 32 debounce counters, and `debounce_time_mt6765`. Device tree must provide the five named IO configuration resources in the expected order.

## Risks

MT8188 has dense, long field tables and several shared register fields, so bit-position mistakes are likely to produce subtle electrical or mux failures. The TDSEL/RDSEL tables add timing-sensitive surface area beyond basic GPIO and bias; tests need to cover these custom configs. `mt8188_pull_type` mixes PU/PD, PUPD/R1R0, and PU/PD/RSEL behavior; mismatch with the register ranges causes generic bias operations to fail or program incomplete state. RSEL supports 3-bit values with several resistance pairs for pins 53-68 and 175-176, so wrong lookup values can affect signal integrity. The driver lacks `MODULE_DEVICE_TABLE(of, ...)`, which is worth checking if module autoloading matters in this tree.

## Test Signals

Signals include build/probe success, all five resources mapped, pinctrl debugfs visibility, GPIO direction/value tests across pins 0-177, pinmux tests for board peripherals, IES/SMT tests across each base, TDSEL/RDSEL custom pinconf tests, bias tests for each pull-type cluster, RSEL tests on pins 53-68 and 175-176, drive and advanced-drive tests, EINT debounce/wake tests, suspend/resume coverage, and module metadata/autoload checks if built as a module.
