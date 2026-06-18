# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa27x.c

## Purpose
Provides the PXA27x-specific pin/function table and platform driver wrapper for the shared PXA2xx pinctrl implementation.

## Important APIs, Types, And Functions
The main data is `pxa27x_pins[]`, a large table of GPIO-capable pins and alternate functions covering UART, SSP, USB, camera, keypad, LCD, AC97/I2S, MMC, memory, and other PXA27x blocks. Runtime code is `pxa27x_pinctrl_probe()`, the OF match table `marvell,pxa27x-pinctrl`, and the module platform driver.

## Control Flow
Probe maps the same register resource layout as PXA25x, computes bank base arrays, and calls `pxa2xx_pinctrl_init()` with PXA27x descriptors. The common implementation derives groups and functions dynamically from the descriptor table and handles all mux/pinconf operations.

## State And Persistence
The file itself is static metadata. Hardware persistence is in PXA27x GAFR, GPDR, and PGSR registers accessed by the common implementation.

## Dependencies And Integration Points
Depends on `pinctrl-pxa2xx.h` macros and `pxa2xx_pinctrl_init()`. It is selected by `CONFIG_PINCTRL_PXA27X` and matched by OF compatible `marvell,pxa27x-pinctrl`.

## Risks
The table contains many repeated function names with different direction and alternate-function values; grouping is name-based, so naming mistakes can merge or split function groups incorrectly. Like PXA25x, resource ordering and derived bank-pointer strides must match platform register layout.

## Test Signals
Compile with `CONFIG_PINCTRL_PXA27X`, probe on PXA27x hardware or emulation, inspect generated function groups, and verify mux programming for high-use blocks such as FFUART, MMC, LCD, camera, and USB pins.
