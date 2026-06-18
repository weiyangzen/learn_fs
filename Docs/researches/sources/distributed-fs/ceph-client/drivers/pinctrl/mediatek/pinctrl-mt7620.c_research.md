# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7620.c

## Purpose
This file is the MT7620/RT2880-family pinmux table for the legacy `pinctrl-mtmips` driver. Unlike the Paris MediaTek mobile SoC files, it does not define per-pin electrical register fields. It declares mux-mode bit encodings and pin groups for common MT7620A peripheral functions, then registers a platform driver for `ralink,mt7620-pinctrl` and the fallback `ralink,rt2880-pinmux`.

## Important APIs, Types, And Functions
The `MT7620_GPIO_MODE_*` macros define shift positions, masks, GPIO fallback encodings, and function mode values for shared mux registers. Function arrays use `struct mtmips_pmx_func` and the `FUNC(name, value, first_pin, pin_count)` macro to describe alternatives such as I2C, SPI, UART lite, MDIO/refclk, RGMII, SPI refclk, EPHY, WLED, PA, UARTF/PCM/I2S combinations, watchdog reset/refclk, PCIe reset/refclk, and NAND/SD.

`mt7620a_pinmux_data` is the key table of `struct mtmips_pmx_group`. `GRP()` entries describe simple one-bit or direct mode selections, while `GRP_G()` entries include a mask, GPIO value, and shift for multi-bit groups. `mt7620_pinctrl_probe()` passes that table to `mtmips_pinctrl_init()`.

## Control Flow
`core_initcall_sync(mt7620_pinctrl_init)` registers the platform driver early and synchronously. On OF match, `mt7620_pinctrl_probe()` calls the shared MIPS pinctrl initializer with `mt7620a_pinmux_data`. The common `pinctrl-mtmips` code then exposes each group/function to pinctrl consumers and writes the SoC's global GPIO mode register fields when a function is selected.

## State And Persistence
This file contains static function/group tables only. Runtime state is held in the MT7620 GPIO mode register bits written by the shared mtmips driver. Because several peripheral blocks share pins and multi-bit encodings, selecting one function persists by excluding other functions in the same group until another state rewrites the group.

## Dependencies And Integration Points
The file depends on Linux module/platform/OF headers and `pinctrl-mtmips.h` for table types, macros, and `mtmips_pinctrl_init()`. It integrates with device-tree pinctrl states used by Ralink/MediaTek MIPS platform devices such as Ethernet, MDIO, PCIe, NAND/SD, UART, SPI, I2C, and LEDs.

## Risks
Shared mux groups are the main risk. UARTF, PCM, I2S, and GPIO alternatives overlap heavily and use a three-bit field; a wrong mode value can partially enable the wrong peripheral. Some groups use `GRP_G()` with explicit GPIO fallback values, so mask/shift mistakes can leave pins unavailable as GPIO. The compatible fallback to `ralink,rt2880-pinmux` means board DTS files may bind this table through a generic compatible, so behavioral changes can affect older boards.

## Test Signals
Validation should include boot binding, pinctrl debugfs group/function listing, and device-tree states for every group. Functional smoke tests should cover I2C, SPI, UART lite, UARTF alternatives, MDIO/refclk, RGMII1/RGMII2, PCIe reset/refclk, watchdog, NAND/SD selection, WLED, EPHY, and PA. GPIO fallback should be tested for every `GRP_G()` group.
