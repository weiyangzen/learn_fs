# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6397.h

## Purpose

`pinctrl-mtk-mt6397.h` describes the 41 GPIO-capable pins exposed by the MediaTek MT6397 PMIC pin controller. It defines `mtk_pins_mt6397[]`, a `static const struct mtk_desc_pin` array used by the MT6397 pinctrl platform driver to expose PMIC pins to Linux pinctrl and GPIO consumers.

Unlike the application-processor SoC tables in this directory, this table is for an MFD child of the MT6397 PMIC. The companion `.c` driver obtains the parent `mt6397_chip` regmap and calls `mtk_pctrl_init` with this descriptor table and PMIC register offsets.

## Important APIs, Types, And Data

The file uses the older `pinctrl-mtk-common.h` descriptor interface:

- `MTK_PIN(PINCTRL_PIN(number, name), pad, "mt6397", eint, functions...)` creates one `struct mtk_desc_pin`.
- `MTK_EINT_FUNCTION()` records external interrupt support. The table has 41 EINT descriptors, 25 real EINT-capable pins, and 16 `NO_EINT_SUPPORT` pins.
- `MTK_FUNCTION()` lists mux options. The table contains 209 function descriptors using mux values 0 through 7.

Pins 0-11 cover PMIC interrupt, source-voltage enable, clock/event, SPI, and audio signals. Pins 12-36 cover keypad columns/rows, PWM, I2C, and EINT alternate functions. Pins 37-40 expose HDMI/DDC/hotplug/CEC style functions. GPIO mode is represented as mux value 0 for every pin.

## Control Flow And Runtime Use

This header is included by `pinctrl-mt6397.c`. During `mt6397_pinctrl_probe`, the driver gets the parent PMIC object with `dev_get_drvdata(pdev->dev.parent)` and passes `mt6397->regmap` plus `mt6397_pinctrl_data` into `mtk_pctrl_init`.

The common pinctrl code then uses this table to register PMIC pins, enumerate per-pin functions, resolve GPIO requests, and apply pinmux or pinconf operations through the PMIC regmap. Because this is an MFD child, register I/O does not go through an MMIO resource owned by the pinctrl device; it goes through the parent regmap with offsets rooted at `MT6397_PIN_REG_BASE`.

## State And Persistence Behavior

The header is immutable descriptor data. It stores no runtime state and performs no writes. Hardware state is persisted only in the MT6397 register map after the common driver writes direction, pull enable/select, data out, and pinmux registers. The descriptor table controls what the driver considers valid, but it does not cache the resulting register values.

## Dependencies And Integration Points

Direct dependencies are `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. The companion driver also depends on `<linux/mfd/mt6397/core.h>` to access the parent PMIC regmap.

Key integration points are the `mediatek,mt6397-pinctrl` compatible, `mt6397_pinctrl_data`, and the PMIC register offsets in `pinctrl-mt6397.c`. That data marks input-enable and Schmitt-trigger offsets as `MTK_PINCTRL_NOT_SUPPORT`, so generic pin configuration requests for those features should fail rather than touching unsupported registers.

## Risks And Edge Cases

The table is small but binding-sensitive. EINT mappings begin at pin 12 with mux value 2 and non-contiguous EINT numbers that must agree with PMIC interrupt wiring. Incorrect mapping can break keypad, hotplug, or wake-related use cases. GPIO and special function names are consumed by DTS pinctrl states and by debug tools, so renaming can break existing boards.

Because the register base is a PMIC regmap, an incorrect descriptor can drive pins that may be involved in power sequencing, clocks, or HDMI/CEC behavior. Unsupported input-enable and Schmitt controls are explicitly marked in the `.c` data; tests should ensure this header does not imply those capabilities indirectly through function naming.

## Test Signals

Validation signals include successful probe of the `mediatek-mt6397-pinctrl` MFD child, successful GPIO requests for pins 0-40, and expected pinctrl debugfs output for `INT`, SPI, audio, keypad, PWM, I2C, HDMI, hotplug, and CEC pins. Tests should exercise PMIC-backed register writes through regmap, verify unsupported input-enable/Schmitt requests fail cleanly, and confirm EINT-capable pins 12-36 can trigger interrupts with the documented mux setting.
