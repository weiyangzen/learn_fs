# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs3.c

## Purpose

This file provides the Socionext UniPhier PXs3 pinctrl hardware description. It supplies pin descriptors, pin groups, functions, GPIO range data, a PXs3-specific GPIO mux callback, capability flags, and platform-driver registration for `socionext,uniphier-pxs3-pinctrl`.

The source is data-heavy and is intended to be consumed by the common UniPhier pinctrl implementation.

## Important APIs, Types, And Data

- `uniphier_pxs3_pins[]` enumerates PXs3 pins and packs per-pin electrical controls into `drv_data` with `UNIPHIER_PINCTRL_PIN`.
- Groups cover audio input/output and IEC pins, eMMC with DAT8, two Ethernet controllers with RGMII/RMII choices (`ether_*` and `ether1_*`), I2C, NAND, SD, SPI, system bus, UART with CTS/RTS and modem extras, and USB host/device pins.
- `gpio_range0_pins[]`, `gpio_range1_pins[]`, and `gpio_range2_pins[]` expose sparse GPIO pin ranges.
- `uniphier_pxs3_groups[]` stores the group descriptors, including mux value lists.
- `uniphier_pxs3_functions[]` maps function selectors to group names.
- `uniphier_pxs3_get_gpio_muxval()` contains PXs3’s special XIRQ/GPIO mapping.
- `uniphier_pxs3_pindata` sets `.caps = UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, indicating per-pin input-enable behavior is available to the common driver.

## Control Flow

The platform driver binds to `socionext,uniphier-pxs3-pinctrl` and calls `uniphier_pinctrl_probe()` with PXs3 data. The common driver registers pinctrl objects and later uses group/function mappings when device-tree pin states are selected.

For GPIO request routing, `uniphier_pxs3_get_gpio_muxval()` returns `0` for XIRQ GPIO offsets `120..143` when the physical pin is in `219..234`, returns `14` for the remaining XIRQ offsets, and returns `15` for ordinary GPIO offsets. This makes PXs3 more nuanced than PXs2 because some XIRQ-capable pins use a GPIO mux value of zero.

## State And Persistence

There is no mutable state in this file. It provides immutable descriptors and callback logic. Hardware register state persists in the pin controller and is manipulated by the common driver during pinmux, GPIO, and pinconf operations.

## Dependencies And Integration Points

The source depends on `pinctrl-uniphier.h` for macros and `struct uniphier_pinctrl_socdata`. It integrates with the Linux platform/OF subsystem through `socionext,uniphier-pxs3-pinctrl` and with generic pinctrl through the shared UniPhier implementation.

The `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL` capability is a key integration signal: the common driver must use per-pin input-enable control rather than a simpler global assumption.

## Risks And Edge Cases

- The special GPIO mux callback has two dimensions, GPIO offset and physical pin number. Bugs in GPIO range tables can produce incorrect muxing even if the callback is unchanged.
- Dual Ethernet controller descriptions and overlapping audio/UART alternatives increase the risk of pin conflicts in board device trees.
- Per-pin input-enable capability means pin descriptor metadata is more important for electrical correctness.
- Mux value tables are static hardware constants; compile-time array-size checks do not prove they match silicon.

## Test Signals

Good test signals are successful probe, selection of both Ethernet controllers in RGMII and RMII modes, eMMC DAT8, SD, NAND, audio, UART CTS/RTS/modem, and USB host/device pin states. GPIO tests should cover normal GPIOs, XIRQ offsets outside pin range `219..234`, and XIRQ offsets on pins `219..234` to verify both special return paths.
