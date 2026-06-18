# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld11.c

## Purpose

This file supplies the UniPhier LD11 SoC-specific pin controller data and platform-driver binding. It is table-driven data for the shared UniPhier core rather than an independent pinctrl algorithm implementation.

## Important APIs, Types, And Functions

The file defines `uniphier_ld11_pins` with 149 `UNIPHIER_PINCTRL_PIN()` descriptors, 41 mux groups, 6 GPIO-only groups, and 27 pinmux functions. Peripheral groups cover audio input/output and IEC variants, eMMC, RMII Ethernet, HSC input/output variants, I2C, NAND, SPI, system bus, UARTs with optional CTS/RTS and modem pins, and USB VBUS/overcurrent pins.

`uniphier_ld11_get_gpio_muxval()` maps GPIO requests to UniPhier mux values: GPIO offsets 132 and 135, representing XIRQ12 and XIRQ15, use mux value 13; GPIO offsets 120 through 143 use mux value 14; all other GPIOs use mux value 15. `uniphier_ld11_pindata` packages the pins, groups, functions, GPIO mux callback, and `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`. `uniphier_ld11_pinctrl_probe()` forwards that data to the shared `uniphier_pinctrl_probe()`. The OF compatible is `socionext,uniphier-ld11-pinctrl`.

## Control Flow

At built-in platform-driver registration, a matching DT node invokes the LD11 probe wrapper, which calls the shared core. The core registers pinctrl operations, exposes all LD11 groups and functions, parses generic pinconf properties, and uses LD11's packed pin descriptors for drive, pull, and input-enable register addressing. Runtime mux changes select each group's pin list and LD11-specific mux values; GPIO requests call `uniphier_ld11_get_gpio_muxval()` before programming the mux.

## State And Persistence

The LD11 file owns no mutable state. Its pin, group, function, and match tables are `static const`. Runtime state lives in the shared UniPhier core and hardware registers. Because the SoC data advertises per-pin input-enable control, the core treats input-enable bits as keyed by pin number for configuration and suspend/resume sizing.

## Dependencies And Integration Points

This source depends on `pinctrl-uniphier.h`, Linux platform-driver and OF match infrastructure, and the shared UniPhier core. It integrates with board device trees through the LD11 compatible string and through pinctrl state names matching the function and group names declared here.

## Risks

Most risk is descriptor accuracy. The file mixes ordinary peripheral groups, optional width extensions such as `emmc_dat8`, GPIO-only ranges, and overlapping alternate functions. A wrong pin number or mux value can silently route a board peripheral to another pad. The XIRQ-specific GPIO mux exceptions must match the GPIO controller's range IDs; if a range ID changes, `gpio_offset`-based selection can choose the wrong mux value. Per-pin input-enable capability must remain aligned with LD11 hardware.

## Test Signals

Good validation includes DT probe with `socionext,uniphier-ld11-pinctrl`, successful application of eMMC, NAND, RMII, UART, SPI, I2C, USB, audio, and system-bus pin states, GPIO tests through every declared GPIO range, XIRQ GPIO tests for offsets 120-143 and special offsets 132/135, bias and drive tests on 1-bit, 2-bit, fixed4, and fixed5 pins, and suspend/resume checks that per-pin input-enable settings survive.
