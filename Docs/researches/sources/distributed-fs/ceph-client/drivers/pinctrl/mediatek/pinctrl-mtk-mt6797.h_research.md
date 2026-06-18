# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6797.h

## Purpose

`pinctrl-mtk-mt6797.h` defines the MT6797 pin descriptor table for the MediaTek Paris pinctrl framework. It contributes `mtk_pins_mt6797[]`, a 262-entry `static const struct mtk_pin_desc` array covering GPIO0 through GPIO261. Each entry provides the pin name, EINT descriptor, drive group, and mux-function alternatives.

The header is included by `pinctrl-mt6797.c`, which is based on the MT6765 driver but supplies a much smaller pin configuration register model for MT6797.

## Important APIs, Types, And Data

This file uses the Paris descriptor macros:

- `MTK_PIN(number, "GPIOx", MTK_EINT_FUNCTION(...), DRV_GRP3, functions...)` creates each pin descriptor.
- Every entry uses `DRV_GRP3`, so the table has a uniform drive-strength class.
- Every EINT descriptor is `MTK_EINT_FUNCTION(NO_EINT_SUPPORT, NO_EINT_SUPPORT)`. The table has no real EINT-capable pins, even though many mux function names contain `EINT` as peripheral signal names.
- `MTK_FUNCTION()` supplies mux values 0 through 7, with GPIO mode at 0.

The table contains 262 pins and 1099 function descriptors. It heavily covers camera/MIPI CSI, debug monitor, SPI, connectivity, C2K, BPI, JTAG, modem, MSDC, DPI/display, I2S/audio, UART, PCM, antenna selection, clock monitor, SCP, and LTE/DFD debug functions. The final pins are JTAG-oriented GPIO257-GPIO261.

## Control Flow And Runtime Use

`pinctrl-mt6797.c` assigns this table to `mt6797_data` and probes through `mtk_paris_pinctrl_probe` for `mediatek,mt6797-pinctrl`. The Paris driver uses the descriptors to expose the pins and per-pin function lists.

Unlike MT6765/MT6779/MT6795, the companion `.c` file only provides register calculators for MODE, DIR, DI, and DO. It names five register bases: `gpio`, `iocfgl`, `iocfgb`, `iocfgr`, and `iocfgt`. Therefore this header's mux information is available, but advanced pinconf features such as bias, drive, input-enable, and Schmitt are not described by MT6797 register calculators in this driver.

## State And Persistence Behavior

The header is static descriptor data and contains no mutable runtime state. Runtime state is limited to the Paris pinctrl device, GPIO chip state, and hardware mode/direction/data registers. Because EINT support is absent in this table and no EINT hardware data is provided in `mt6797_data`, interrupt state is not built from this header.

## Dependencies And Integration Points

The direct include is `pinctrl-paris.h`. Integration occurs through `pinctrl-mt6797.c`, whose SoC data sets `.pins`, `.npins`, `.ngrps`, `.gpio_m = 0`, and base-name metadata but does not set `.eint_hw` or pinconf operation hooks.

Device-tree pinctrl states must use names and mux choices from this table. Since many functions are high-speed or debug signals, board DTS files need to match the exact pad capabilities. The absence of EINT support should be reflected in board designs that require GPIO interrupts.

## Risks And Edge Cases

The key edge case is that function names include `EINT`-looking peripheral names such as C2K-related signals, but the actual `struct mtk_eint_desc` values are all `NO_EINT_SUPPORT`. Consumers must not infer Linux GPIO interrupt support from function-string names.

Another risk is overexposing pinconf expectations. The header contains drive group values, but the companion driver only registers MODE, DIR, DI, and DO register calculators and no explicit drive/bias callbacks. Tests should verify unsupported pinconf requests fail cleanly. With 262 pins and many mux alternatives, typographical errors in function strings or pin-number alignment errors can affect camera, display, modem, connectivity, and debug interfaces.

## Test Signals

Validation signals include a clean build, successful `mt6797-pinctrl` probe, debugfs enumeration of 262 pins/groups, and correct GPIO mode/direction/data behavior for low and high pin numbers. Pinmux tests should focus on camera/MIPI CSI, SPI, MSDC, display DPI, audio/I2S, UART, connectivity, and JTAG/debug pins. Negative tests should confirm GPIO-to-IRQ/EINT requests are unsupported and that bias/drive/Schmitt/input-enable pinconf operations are not falsely advertised by this SoC data.
