# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro5.c

## Purpose

This file is the Socionext UniPhier Pro5 SoC pinctrl data provider. It supplies the common UniPhier pinctrl core with the Pro5 pin descriptor table, pin groups, pinmux functions, GPIO mux policy, capability flags, OF match table, and platform driver registration for `socionext,uniphier-pro5-pinctrl`.

The file is almost entirely declarative hardware description. Runtime behavior is limited to the SoC-specific GPIO mux value callback, the thin probe wrapper, and builtin platform-driver registration.

## Important APIs, Types, And Data

- `uniphier_pro5_pins[]` is a large `struct pinctrl_pin_desc` array created with `UNIPHIER_PINCTRL_PIN`. Each entry encodes pin number, name, input-enable control, drive-strength control register, drive type, pull register, and pull direction into `drv_data`.
- Group pin arrays cover Pro5 peripheral signals including `emmc`, `emmc_dat8`, I2C controllers `i2c0` through `i2c6` with several `i2c5` alternatives, `nand` plus `nand_cs1`, `pcie`, `sd`, `spi0` to `spi2`, `system_bus` plus chip-select extensions, UART groups including alternate/modem groups, and `usb0` to `usb2`.
- `gpio_range_pins[]` lists sparse pin numbers used to expose GPIO ranges through the common driver.
- `uniphier_pro5_groups[]` maps each named group to its pin list and mux-value list with `UNIPHIER_PINCTRL_GROUP` or GPIO-only group semantics.
- `uniphier_pro5_functions[]` maps Linux pinmux function names to the groups each function may select.
- `uniphier_pro5_get_gpio_muxval()` returns the mux value used when a pin is requested as GPIO.
- `uniphier_pro5_pindata` packages the arrays and callback as `struct uniphier_pinctrl_socdata`.

## Control Flow

At boot or device creation, the builtin platform driver matches `socionext,uniphier-pro5-pinctrl`. `uniphier_pro5_pinctrl_probe()` calls `uniphier_pinctrl_probe(pdev, &uniphier_pro5_pindata)`. The common UniPhier driver then uses the data arrays to register pins, groups, functions, GPIO ranges, pinconf, and pinmux operations.

When a non-GPIO function is selected, the common driver consumes the group descriptor and writes the corresponding mux values for each group pin. When a pin is requested as GPIO, the common driver calls `uniphier_pro5_get_gpio_muxval(pin, gpio_offset)`. Pro5 returns mux value `14` for GPIO offsets `120..141` representing XIRQ lines and `15` otherwise.

## State And Persistence

The file has no mutable module state. Persistent hardware state is the SoC pin controller register state written by the common UniPhier core. All arrays are `static const`, and allocations, locks, and register mappings are owned by the shared driver. The packed per-pin `drv_data` is immutable metadata.

## Dependencies And Integration Points

This file depends on `pinctrl-uniphier.h` for the descriptor macros, `struct uniphier_pinctrl_socdata`, and `uniphier_pinctrl_probe()`. It integrates with the Linux platform bus through `struct platform_driver`, OF matching, and `builtin_platform_driver`. It also depends on the generic Linux pinctrl subsystem indirectly through the common UniPhier driver.

The `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE` flag tells the common driver that debug mux handling is separate on this SoC. GPIO mux semantics are integrated through the `get_gpio_muxval` callback.

## Risks And Edge Cases

- Pin numbering and group pin lists must match the hardware manual and device-tree binding expectations; a wrong entry can silently route a board signal to the wrong function.
- `gpio_range_pins[]` is sparse and must remain aligned with GPIO offset assumptions in `uniphier_pro5_get_gpio_muxval()`.
- XIRQ GPIO offsets use a distinct mux value. Regressions here can break interrupt-capable pins while ordinary GPIO pins still work.
- The descriptor macros perform some compile-time array length checks for group pin/mux arrays, but they cannot validate hardware register offsets or mux values.

## Test Signals

Useful verification signals include successful boot-time probe for `socionext,uniphier-pro5-pinctrl`, absence of pinctrl registration errors, device-tree pinmux selection for eMMC, SD, NAND, SPI, UART, and USB groups, GPIO request tests for normal GPIO and XIRQ offsets, and pinconf validation for drive strength, pull direction, and input-enable behavior through the common UniPhier code.
