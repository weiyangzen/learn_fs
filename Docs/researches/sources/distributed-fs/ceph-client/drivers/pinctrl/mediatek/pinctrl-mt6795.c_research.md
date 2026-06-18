# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6795.c

## Purpose
This file is the MT6795 pinctrl data provider for the MediaTek Paris driver. It describes a 197-pin SoC using an older register layout with 15-bit and 16-bit field packing, explicit pull-enable/pull-select registers, selected PUPD/R0/R1 advanced pull fields, slew-rate control, EINT hardware, and PM-aware platform-driver registration.

## Important APIs, Types, And Functions
`PIN_FIELD15()`, `PIN_FIELD16()`, and `PINS_FIELD16()` wrap `PIN_FIELD_CALC()` with a single base index and 15- or 16-bit field stride. Basic GPIO controls are defined by `mt6795_pin_dir_range`, `mt6795_pin_pullen_range`, `mt6795_pin_pullsel_range`, `mt6795_pin_do_range`, `mt6795_pin_di_range`, and `mt6795_pin_mode_range`. Electrical configuration arrays cover IES, SMT, PUPD, R0, R1, drive strength, and slew rate.

`mt6795_reg_cals` exposes those arrays to the generic `PINCTRL_PIN_REG_*` lookup path. `mt6795_eint_hw` declares seven EINT ports, 224 AP EINT lines, 32 debounce counters, and `debounce_time_mt6795`. `mt6795_pull_type` is a per-pin policy table selecting `MTK_PULL_PULLSEL_TYPE` or `MTK_PULL_PUPD_R1R0_TYPE`, which is critical because the SoC uses both legacy pullsel and advanced resistor-controlled pull models. `mt6795_data` wires rev1 bias/drive callbacks, combo bias helpers, advanced pull helpers, `nfuncs = 8`, and the default MediaTek register base names.

## Control Flow
The init function `mtk_pinctrl_init()` is registered with `arch_initcall()` and registers `mt6795_pinctrl_driver`. OF matching on `mediatek,mt6795-pinctrl` supplies `mt6795_data` to `mtk_paris_pinctrl_probe()`. The driver also attaches `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`, so system sleep state handling is delegated to the shared Paris PM operations when PM sleep is enabled.

## State And Persistence
No local runtime objects are allocated by this file. Static range tables and the pull-type array determine how the common driver mutates hardware state. Persistent hardware effects include mux mode, GPIO direction/data, pull enable/select, advanced pull resistor bits, Schmitt trigger, input-enable, drive strength, slew rate, and EINT debounce settings.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6795.h` for `mtk_pins_mt6795` and debounce metadata, `pinctrl-paris.h` for the core implementation and rev1 pinconf helpers, the platform bus, and OF compatible matching. It integrates with pinctrl, gpiolib, IRQ/EINT handling, and PM sleep pin-state transitions.

## Risks
MT6795 has mixed pull models, so an incorrect `mt6795_pull_type` entry can route generic bias requests to the wrong register family. Some field tables contain peripheral-specific regions for keypad, DPI, and MSDC pins; mistakes in these ranges can break high-speed interfaces while ordinary GPIO tests still pass. The 15-bit mode packing and 16-bit control packing are unusual compared with newer 32-bit Paris SoCs, making stride and bit-width regressions likely when refactoring macros.

## Test Signals
Good signals include boot binding for `mediatek,mt6795-pinctrl`, pinctrl debugfs showing 197 pins and eight functions, GPIO tests for mode/direction/data, pull configuration tests on both legacy pullsel pins and PUPD/R0/R1 pins, drive/slew readback, EINT tests across multiple ports and debounce counters, and suspend/resume testing to exercise the Paris PM ops.
