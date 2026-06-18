# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6779.h

## Purpose

`pinctrl-mtk-mt6779.h` is the MT6779 pin descriptor table for the MediaTek Paris pinctrl framework. It defines `mtk_pins_mt6779[]`, a 210-entry `static const struct mtk_pin_desc` array covering GPIO0 through GPIO209. Each entry records the pin's EINT mapping, drive group, and mux-function set.

The header is paired with `pinctrl-mt6779.c`, which provides register field ranges, EINT hardware sizing, base-name mapping, and platform-driver registration for `mediatek,mt6779-pinctrl`.

## Important APIs, Types, And Data

The table uses the Paris `MTK_PIN` API:

- `MTK_PIN(number, "GPIOx", MTK_EINT_FUNCTION(...), DRV_GRPn, MTK_FUNCTION(...))` creates a `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(0, eint_number)` maps pins to AP EINT lines; unsupported pins use `NO_EINT_SUPPORT`.
- `DRV_GRP4` is used for most pins, while 6 pins use `DRV_GRP0`.
- `MTK_FUNCTION()` lists mux values 0 through 7, with GPIO mode at 0.

The file contains 210 pin descriptors and 1019 function descriptors. It has broad peripheral coverage: SPI, connectivity, JTAG, BPI, SCP, MSDC, I2S, antenna selection, modem, DPI/MIPI/display, TDM/PCM/audio, UART, keypad, PWM, and debug monitor signals. EINT coverage is high: 194 real mappings and 16 unsupported entries.

## Control Flow And Runtime Use

At probe, `pinctrl-mt6779.c` passes `mtk_pins_mt6779` through `mt6779_data` into `mtk_paris_pinctrl_probe`. The Paris driver uses this table to create one group per pin, expose the per-pin mux functions, and resolve pinconf or pinmux requests from device-tree states.

The companion `.c` file supplies register calculators for MODE, DIR, DI, DO, SMT, IES, PU, PD, DRV, PUPD, R0, and R1. Its base names are `gpio`, `iocfg_rm`, `iocfg_br`, `iocfg_lm`, `iocfg_lb`, `iocfg_rt`, `iocfg_lt`, and `iocfg_tl`; this header's pin numbers are the lookup keys into those ranges.

## State And Persistence Behavior

This header is read-only compiled-in capability data. It does not allocate memory, persist configuration, or write registers. Runtime changes happen when pinctrl and GPIO callbacks program SoC registers through the Paris common driver. The pin/function/EINT descriptors constrain which operations are accepted and how names resolve to mux values.

## Dependencies And Integration Points

The direct include is `pinctrl-paris.h`. Integration is through `pinctrl-mt6779.c`, whose `mt6779_data` sets `.ies_present = true`, 195 AP EINTs, 6 EINT ports, 13 debounce counters, and generic combo bias/raw drive/advanced pull operations.

Device-tree integration depends on the `mediatek,mt6779-pinctrl` compatible and on pin/function names matching DTS pinctrl states. EINT integration depends on `mtk_build_eint` and the EINT hardware description from the `.c` file.

## Risks And Edge Cases

The table has some tail entries where mux value 0 is represented as `NULL` rather than a printable GPIO function name. That may be intentional for reserved pins, but it is a notable debugfs and lookup edge case. EINT numbering is mostly dense but not identical to pin numbering near the end, so automated assumptions about `pin == eint` would be wrong.

Large mux lists increase risk of typographical binding regressions. The `.h` table and `.c` register calculators must agree on pin range coverage through GPIO209; otherwise pinctrl may expose a valid function but fail to program the corresponding field. Drive group misclassification can lead to wrong current limits, and incorrect EINT entries can break wakeup-capable GPIOs.

## Test Signals

Expected test signals are successful build/probe for `mt6779-pinctrl`, debugfs enumeration of 210 pins, no missing register-range warnings when applying pin states, and working mux for common DTS users such as SPI, I2S, MSDC, display, connectivity, and modem interfaces. EINT tests should include late-numbered pins such as GPIO206-GPIO209, while debugfs or pinmux self-checks should verify that `NULL` function names do not break function enumeration paths.
