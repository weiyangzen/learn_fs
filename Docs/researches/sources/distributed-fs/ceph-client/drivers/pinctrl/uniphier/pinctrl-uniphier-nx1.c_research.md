# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-nx1.c

## Purpose

This file provides the UniPhier NX1 SoC pinctrl description and platform-driver binding for the shared UniPhier pinctrl core.

## Important APIs, Types, And Functions

`uniphier_nx1_pins` defines 96 pin descriptors. The file declares 23 mux groups, 5 GPIO-only groups, and 19 functions. It covers eMMC with `emmc_dat8`, RGMII/RMII Ethernet, I2C0-I2C6, SD, SPI0/SPI1, UART0-UART3 with UART1 and UART2 flow-control extensions, and USB0/USB1. Some eMMC mux values are `-1`, indicating dedicated pins that the shared core input-enables but does not program through the pinmux registers.

`uniphier_nx1_get_gpio_muxval()` returns mux value 14 for GPIO offsets 120 and above, treated as XIRQ lines, and mux value 15 otherwise. `uniphier_nx1_pindata` enables `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, so the shared core treats input-enable controls as per-pin. The OF compatible is `socionext,uniphier-nx1-pinctrl`.

## Control Flow

Probe is a wrapper that calls the shared `uniphier_pinctrl_probe()` with the NX1 data. After registration, DT pinctrl states select groups by name and the core writes each group's mux values. GPIO request handling uses the NX1 GPIO mux callback before the shared one-pin mux path. Generic pinconf get/set operations use the NX1 packed pin attributes.

## State And Persistence

The file owns only static const SoC metadata. Runtime state and persistence rules are inherited from the shared core and hardware registers. Per-pin input-enable capability means the core uses pin numbers for input-enable bits, including suspend/resume save sizing.

## Dependencies And Integration Points

NX1 integrates through the platform driver's OF match table, the shared UniPhier core, Linux pinctrl and GPIO range handling, and board DT pinctrl states that reference the declared group/function names.

## Risks

Because NX1 is a smaller table with several dedicated eMMC pins, negative mux handling must be validated for boot-media paths. The broad `gpio_offset >= 120` XIRQ rule assumes the GPIO controller exposes XIRQ offsets at and above 120; a different range layout would choose mux value 14 for the wrong lines. Per-pin input-enable flag accuracy matters for both runtime input-enable and PM restore behavior. I2C4-I2C6 and UART flow-control groups share limited high pads, so board states must avoid incompatible simultaneous selections.

## Test Signals

Signals include successful probe with `socionext,uniphier-nx1-pinctrl`, eMMC and `emmc_dat8` state application with negative mux values, RGMII/RMII Ethernet tests, I2C0-I2C6 and UART flow-control mux tests, GPIO request tests on offsets below and above 120, pinconf bias/drive/input-enable tests, and suspend/resume validation on per-pin input-enable registers.
