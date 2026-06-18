# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-sld8.c

## Purpose

This file is the UniPhier SLD8 SoC pinctrl data provider. It describes SLD8 pins, peripheral groups, pinmux functions, sparse GPIO ranges, the SLD8 GPIO mux callback, and the platform driver for `socionext,uniphier-sld8-pinctrl`.

The implementation is declarative data plus a small GPIO mux function and a probe wrapper into the common UniPhier pinctrl driver.

## Important APIs, Types, And Data

- `uniphier_sld8_pins[]` is the SLD8 pin descriptor table with packed pinconf and mux-control metadata.
- Peripheral groups include `emmc` and `emmc_dat8`, Ethernet MII/RMII, I2C0-I2C3, NAND plus `nand_cs1`, SD, SPI0, system bus plus chip-select extensions, UART groups including CTS/RTS and modem, and USB0-USB2.
- `gpio_range0_pins[]`, `gpio_range1_pins[]`, and `gpio_range2_pins[]` define sparse GPIO-exposed pins.
- `uniphier_sld8_groups[]` and `uniphier_sld8_functions[]` provide the group/function mapping consumed by the common driver.
- `uniphier_sld8_get_gpio_muxval()` handles XIRQ GPIO exceptions through a `switch` over GPIO offsets.
- `uniphier_sld8_pindata` packages all arrays and sets baseline capabilities with `.caps = 0`.

## Control Flow

The builtin platform driver binds to `socionext,uniphier-sld8-pinctrl`. Its probe function calls `uniphier_pinctrl_probe()` with `uniphier_sld8_pindata`.

When a device-tree pin state selects a function, the common driver resolves the function to groups and writes the group mux values. GPIO request handling calls `uniphier_sld8_get_gpio_muxval()`, which returns `0` for XIRQ0-XIRQ7 offsets `120..127`, `14` for XIRQ8-XIRQ12 and XIRQ14-XIRQ15 offsets `128..132` and `134..135`, and `15` for other offsets.

## State And Persistence

The source has no mutable state. Register state lives in hardware and is controlled through the shared UniPhier pinctrl implementation. Static arrays in this file are immutable descriptors.

## Dependencies And Integration Points

The file depends on the UniPhier common header and common probe routine. It integrates with OF using `socionext,uniphier-sld8-pinctrl`, registers as a builtin platform driver, and is consumed by generic Linux pinctrl through the common driver.

SLD8 uses baseline UniPhier capabilities and relies on its SoC-specific GPIO mux callback to distinguish XIRQ offset ranges.

## Risks And Edge Cases

- The XIRQ callback intentionally skips offset `133`; this must match hardware and GPIO range definitions.
- Some pins appear in multiple functional contexts, such as I2C and USB/UART alternatives, so board-level pin states must avoid conflicts.
- System bus chip-select groups are split out; missing an extension group can partially configure an external bus.
- As with other UniPhier data files, hardware constants are not validated by the compiler beyond array shape.

## Test Signals

Probe should succeed for an SLD8 device-tree node. Runtime tests should exercise eMMC DAT8, Ethernet MII/RMII, NAND with chip select, SD, SPI0, system bus chip selects, UART modem/CTSRTS, and USB groups. GPIO tests should cover XIRQ offsets in each callback case and an ordinary GPIO offset.
