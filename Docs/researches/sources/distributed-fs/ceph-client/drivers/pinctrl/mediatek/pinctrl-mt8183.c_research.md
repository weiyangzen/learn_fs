# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8183.c

## Purpose

This file is the MT8183 pinctrl data driver for the newer MediaTek "Paris" pinctrl framework. It describes how each pin property maps to one of nine named MMIO bases and how generic Paris pinctrl callbacks should handle mode, GPIO, IES, SMT, pull, drive, advanced drive, and EINT operations.

## Important APIs, Types, And Functions

The file defines `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrappers around `PIN_FIELD_CALC()` for single-pin and shared-field register calculations. Key data arrays are `mt8183_pin_mode_range`, `mt8183_pin_dir_range`, `mt8183_pin_di_range`, `mt8183_pin_do_range`, `mt8183_pin_ies_range`, `mt8183_pin_smt_range`, `mt8183_pin_pullen_range`, `mt8183_pin_pullsel_range`, `mt8183_pin_drv_range`, `mt8183_pin_pupd_range`, `mt8183_pin_r0_range`, `mt8183_pin_r1_range`, `mt8183_pin_e1e0en_range`, `mt8183_pin_e0_range`, and `mt8183_pin_e1_range`.

`mt8183_reg_cals` maps those arrays to `PINCTRL_PIN_REG_*` indices. `mt8183_data` is the `struct mtk_pin_soc` consumed by `mtk_paris_pinctrl_probe`. It points to `mtk_pins_mt8183`, nine base names, EINT metadata, and generic callbacks such as `mtk_pinconf_bias_set_combo`, `mtk_pinconf_drive_set_rev1`, and advanced drive get/set helpers.

## Control Flow

The platform driver registers at `arch_initcall`. On `mediatek,mt8183-pinctrl`, the Paris probe obtains `mt8183_data` through OF match data, ioremaps every named base resource, builds pinctrl state, registers the pinctrl device, enables it, initializes EINT if possible, and creates the GPIO chip.

Runtime control is completely table-driven. Mode/dir/DI/DO use the primary base style. IES and SMT use per-pin and shared fields over bases `iocfg0` through `iocfg8`. Pull enable and pull select cover normal pull pins. PUPD/R0/R1 arrays support advanced pull pins, and E1/E0/DRV_EN arrays support advanced drive controls.

## State And Persistence

The local data is immutable. Paris runtime state is allocated in `struct mtk_pinctrl`, including the base pointer array, lock, pinctrl state, EINT, and GPIO chip. Register writes persist in hardware until reset, sleep-state loss, or later reconfiguration. The driver uses `.pm = pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`, so Paris EINT suspend/resume hooks participate in PM.

## Dependencies And Integration Points

The source depends on `pinctrl-mtk-mt8183.h` for pin/function descriptors and on `pinctrl-paris.h`/`pinctrl-mtk-common-v2.h` for the range-calculation model. Device tree must provide named resources `iocfg0`, `iocfg1`, `iocfg2`, `iocfg3`, `iocfg4`, `iocfg5`, `iocfg6`, `iocfg7`, and `iocfg8`. EINT metadata advertises six ports, 212 AP interrupt numbers, 13 debounce counters, and `debounce_time_mt6765`.

## Risks

The major risk is base-name and field-table correctness. A wrong `i_base`, offset, bit, or shared-field flag can redirect configuration to another IO configuration block. Some pins have shared fields via `PINS_FIELD_BASE`, so treating them as independent in tests can produce surprising coupled behavior. Advanced pull/drive coverage is sparse and must match the `pull_type` behavior implied by the common Paris code even though this file does not define a pull-type array. Missing any of the nine named resources makes probe fail.

## Test Signals

Test signals include successful build, DT probe with all nine resources mapped, pinmux and GPIO tests across pins 0-192, IES/SMT tests on pins from each `iocfg` base, pull enable/select tests for normal pins, PUPD/R0/R1 tests for advanced-pull pins, advanced drive tests on pins in the E0/E1/DRV_EN tables, EINT debounce tests, and suspend/resume coverage through `mtk_paris_pinctrl_pm_ops`.
