# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6795.h

## Purpose

`pinctrl-mtk-mt6795.h` defines the MT6795 pin descriptor table for the MediaTek Paris pinctrl driver. It exports `mtk_pins_mt6795[]`, a 197-entry `static const struct mtk_pin_desc` array for GPIO0 through GPIO196. The table records each pin's EINT line, drive-strength class, and mux-function options.

The companion `pinctrl-mt6795.c` provides the register layout, pull-type table, EINT hardware data, and platform-driver registration that consume this descriptor table.

## Important APIs, Types, And Data

The descriptor API comes from `pinctrl-paris.h`:

- `MTK_PIN(number, name, eint, drv_n, functions...)` creates each `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(0, n)` maps all 197 pins to real EINT lines 0-196 in this table.
- `DRV_FIXED`, `DRV_GRP0`, `DRV_GRP2`, and `DRV_GRP4` classify drive-strength behavior. The distribution is 6 fixed-drive pins, 54 `DRV_GRP0` pins, 91 `DRV_GRP2` pins, and 46 `DRV_GRP4` pins.
- `MTK_FUNCTION()` records mux options. MT6795 uses mux values 0 through 6 in this header.

The table has 698 function descriptors. Function families include BPI, MSDC, I2S/audio, modem, SPI, DPI/display, JTAG, PWM, LTE, PCM, SIM, UART, DSI/MIPI, camera clocks, and debug/test functions. GPIO mode remains mux value 0.

## Control Flow And Runtime Use

`pinctrl-mt6795.c` includes this file and assigns `.pins = mtk_pins_mt6795`, `.npins = ARRAY_SIZE(mtk_pins_mt6795)`, and `.ngrps = ARRAY_SIZE(mtk_pins_mt6795)` in `mt6795_data`. `mtk_paris_pinctrl_probe` uses the descriptors to register pins/groups and to resolve mux requests.

The `.c` file provides register calculators for MODE, DIR, DI, DO, SR, SMT, DRV, PUPD, R0, R1, IES, PULLEN, and PULLSEL. It also supplies `mt6795_pull_type[]`, which differentiates `MTK_PULL_PULLSEL_TYPE` and `MTK_PULL_PUPD_R1R0_TYPE` per pin. The header's pin ordering is therefore tied to both register calculators and the pull-type array.

## State And Persistence Behavior

The file contains only immutable compiled-in descriptors. Runtime pin state is not stored in this header; it is programmed into hardware registers through Paris pinctrl operations. The driver may read back register state for pinconf queries, but this header remains the static capability map.

## Dependencies And Integration Points

The direct dependency is `pinctrl-paris.h`. The companion driver matches `mediatek,mt6795-pinctrl`, uses the default single `"base"` register name, advertises 224 AP EINTs with 7 ports and 32 debounce counters, and enables Paris PM ops via `mtk_paris_pinctrl_pm_ops`.

The SoC data uses rev1 bias and drive helpers (`mtk_pinconf_bias_*_rev1`, `mtk_pinconf_drive_*_rev1`) plus combo and advanced pull helpers. Because this table supplies all EINT mappings, it is central to GPIO interrupt and wakeup behavior for MT6795 boards.

## Risks And Edge Cases

MT6795 has more varied drive groups and pull types than the simpler Paris tables. Descriptor edits must stay synchronized with `mt6795_pull_type[]`, the register-range arrays, and drive group expectations. All pins declare real EINT support, so an incorrect EINT number is especially likely to cause subtle interrupt routing bugs rather than a clean unsupported error.

The table uses mux values only through 6, unlike many neighboring SoCs that use 0 through 7. Adding a function at value 7 without hardware support would expose invalid pinmux states. Function-string stability matters for DTS users of modem, BPI, display, storage, and audio pins.

## Test Signals

Validation should include successful `mt6795-pinctrl` probe, debugfs enumeration of 197 pins, pinmux coverage for storage, display, modem, SPI, UART, SIM, I2S/PCM, and PWM use cases, and GPIO interrupt tests across low, middle, and high pin numbers. Pinconf tests should cover rev1 bias disable/set/get, pull-select versus PUPD/R0/R1 pins, slew-rate fields, and drive-strength values for `DRV_FIXED`, `DRV_GRP0`, `DRV_GRP2`, and `DRV_GRP4`.
