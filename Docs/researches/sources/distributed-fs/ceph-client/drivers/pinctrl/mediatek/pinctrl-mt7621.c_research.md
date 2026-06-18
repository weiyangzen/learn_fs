# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7621.c

## Purpose
This file describes MT7621 pinmux groups for the legacy `pinctrl-mtmips` framework. It maps global GPIO mode register encodings to named peripheral functions for `ralink,mt7621-pinctrl` and the fallback `ralink,rt2880-pinmux` compatible.

## Important APIs, Types, And Functions
The `MT7621_GPIO_MODE_*` macros define mode bits, masks, shifts, and GPIO fallback values for UARTs, I2C, JTAG, watchdog, PCIe, MDIO, RGMII, SPI, and SDHCI/NAND-related pin groups. Function arrays use `FUNC()` to describe each selectable function and its first pin/count span. Notable multiplexed groups include UART3 versus I2S/SPDIF3, UART2 versus PCM/SPDIF2, SPI versus NAND1, SDHCI versus NAND2, watchdog reset/refclk, and PCIe reset/refclk.

`mt7621_pinmux_data` is the `struct mtmips_pmx_group` table consumed by the common driver. It uses `GRP()` for direct selections and `GRP_G()` for masked multi-bit selections with GPIO fallback values. `mt7621_pinctrl_probe()` passes the table to `mtmips_pinctrl_init()`.

## Control Flow
`core_initcall_sync(mt7621_pinctrl_init)` registers the platform driver. OF matching invokes `mt7621_pinctrl_probe()`, which delegates initialization to `mtmips_pinctrl_init(pdev, mt7621_pinmux_data)`. After that, generic pinctrl state selection flows through the mtmips core, which writes the appropriate mode-field value for the requested group/function.

## State And Persistence
The file is stateless after registration. Hardware state persists in MT7621 global mode bits. Because many groups are mutually exclusive, selecting one function for a group persists until another pinctrl state changes the same masked field.

## Dependencies And Integration Points
It depends on `pinctrl-mtmips.h`, platform-device and OF support, and device-tree consumers using the exposed group/function names. It integrates with serial, I2C, audio, SPDIF, JTAG, watchdog, PCIe, MDIO, Ethernet RGMII, SPI, NAND, and SDHCI platform devices on MT7621 boards.

## Risks
The highest risk is incorrect multi-bit encoding for `GRP_G()` groups. UART2/UART3 audio alternatives, SPI/NAND, and SDHCI/NAND share pins and can break multiple board functions if mask, shift, or GPIO fallback values are wrong. The fallback compatible can broaden the impact of table changes. Since this file contains no pinconf/electrical metadata, consumers must not expect bias or drive control here.

## Test Signals
Test successful binding for both compatibles, debugfs group/function visibility, and mux selection for UART1/2/3, I2C, JTAG, watchdog, PCIe, MDIO, RGMII1/2, SPI/NAND1, and SDHCI/NAND2. GPIO fallback should be verified for masked groups, and board-level tests should cover boot media, network, serial console, and PCIe reset behavior.
