# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8186.c

## Purpose

This file is the MT8186 Paris pinctrl data driver. It maps 185 pins to seven named IO configuration bases and supplies register calculators for mode, GPIO, IES, SMT, pull-up/pull-down, PUPD/R0/R1 pulls, standard drive, advanced drive, resistor selection, and EINT handling.

## Important APIs, Types, And Functions

The file uses local `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` macros to create `struct mtk_pin_field_calc` rows. Important arrays include `mt8186_pin_mode_range`, `mt8186_pin_dir_range`, `mt8186_pin_di_range`, `mt8186_pin_do_range`, `mt8186_pin_ies_range`, `mt8186_pin_smt_range`, `mt8186_pin_pu_range`, `mt8186_pin_pd_range`, `mt8186_pin_pupd_range`, `mt8186_pin_r0_range`, `mt8186_pin_r1_range`, `mt8186_pin_drv_range`, `mt8186_pin_drv_adv_range`, `mt8186_pin_rsel_range`, `mt8186_pin_rsel_val_range`, and `mt8186_pull_type`.

`mt8186_reg_cals` connects those arrays to `PINCTRL_PIN_REG_*` slots, including `PU`, `PD`, `PUPD`, `R0`, `R1`, `DRV_ADV`, and `RSEL`. `mt8186_data` provides the `struct mtk_pin_soc` for `mtk_paris_pinctrl_probe`, with callbacks for combo bias handling, rev1 drive handling, raw advanced drive handling, and pin resistance lookup.

## Control Flow

The driver registers at `arch_initcall` and matches `mediatek,mt8186-pinctrl`. The Paris probe retrieves `mt8186_data`, ioremaps the seven base resources, builds the pinctrl state, registers and enables pinctrl, attempts EINT setup, then registers the GPIO chip.

Runtime operations use the generic Paris pinctrl and pinconf code. Basic GPIO and mux operations use mode/dir/DI/DO ranges. Bias configuration dispatches according to `mt8186_pull_type`: pins 0-66 and many later pins use PU/PD, pins 67-82 and 84-89 use PUPD/R0/R1, and pins 127-146 use PU/PD plus RSEL resistance selection. Drive uses standard 3-bit fields, while advanced drive and RSEL are defined for a narrower high-speed pin subset.

## State And Persistence

Local data is static const, including a complete per-pin pull-type array. Runtime state lives in the Paris core allocation, ioremapped base array, lock, pinctrl device, EINT object, and GPIO chip. Hardware settings are register state, not software persistence. The driver uses `mtk_paris_pinctrl_pm_ops` for suspend/resume of EINT-related state.

## Dependencies And Integration Points

Dependencies include `pinctrl-mtk-mt8186.h`, `pinctrl-paris.h`, common v2 MediaTek pinctrl definitions, Linux platform/OF resource mapping, pinctrl/GPIO, and EINT. Device tree must provide `iocfg0`, `iocfg_lt`, `iocfg_lm`, `iocfg_lb`, `iocfg_bl`, `iocfg_rb`, and `iocfg_rt`. EINT metadata reports seven ports, 217 AP interrupt numbers, 32 debounce counters, and `debounce_time_mt6765`.

## Risks

The large one-entry-per-pin IES/SMT/PU/PD/drive tables create high risk for transcription errors. `mt8186_pull_type` must have exactly one entry per pin and must agree with the presence or absence of PU/PD, PUPD/R0/R1, and RSEL ranges. RSEL values are exposed in ohms-like pairs through `PIN_RSEL`; wrong values affect electrical bias, not just register readability. Named base ordering must match DT resource names because all table `i_base` values are positional.

## Test Signals

Useful tests include build/probe with all seven named resources, pinctrl debugfs inspection, GPIO/mux tests across all 185 pins, bias tests for each pull type cluster, RSEL tests on pins 127-146 including the optional `mediatek,rsel-resistance-in-si-unit` behavior in the Paris core, drive and advanced-drive tests on high-speed pins, EINT interrupt/debounce tests across seven ports, and suspend/resume wake tests.
