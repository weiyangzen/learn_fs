# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld4.c

## Purpose

This file is the UniPhier LD4 SoC pinctrl data provider. It describes LD4 pins, mux groups, functions, GPIO mux value policy, and the platform-driver binding for the shared UniPhier pinctrl core.

## Important APIs, Types, And Functions

`uniphier_ld4_pins` defines 175 pin descriptors. The file declares 28 mux groups, one GPIO-only group, and 18 functions. Major functions include eMMC and `emmc_dat8`, MII and RMII Ethernet, I2C0-I2C3, NAND with chip-select extension, SD, SPI0, system bus with multiple chip-select groups, UART0 with flow/modem extensions, UART1 plus alternate `uart1b`, UART2, UART3, and USB0/USB1/USB2 plus `usb2b`.

`uniphier_ld4_get_gpio_muxval()` has a switch-based policy. PORT00-PORT26, XIRQ1-XIRQ11, and XIRQ14 use mux value 0; XIRQ0, XIRQ12, and XIRQ15 use mux value 14; all other GPIO offsets use mux value 15. `uniphier_ld4_pindata` sets `.caps = 0`, so the shared core uses packed input-enable indices and the non-debug-separate mux layout. The OF compatible is `socionext,uniphier-ld4-pinctrl`.

## Control Flow

The built-in platform driver probes on the LD4 compatible and calls `uniphier_pinctrl_probe()`. The shared core exposes the LD4 functions and groups, handles DT pinctrl maps, and programs mux, bias, drive, and input-enable registers using the LD4 tables. GPIO requests pass through the LD4-specific GPIO mux callback and then through the shared one-pin mux writer.

## State And Persistence

This file contains only static tables and no writable state. Runtime state is stored in the shared pinctrl device and hardware registers. With `.caps = 0`, input-enable controls may be shared across pins; the shared core rejects per-pin disabling in that model and sizes suspend/resume input-enable save ranges from packed `iectrl` values.

## Dependencies And Integration Points

Dependencies are the shared UniPhier header/core, Linux platform and OF support, and board DT pinctrl users. The group and function names are the public integration surface for device-tree pinctrl states.

## Risks

The LD4 groups include negative mux values for dedicated pins in system-bus-related groups, which relies on the shared core's "nothing to write" handling for mux value `< 0`. Several peripherals share pins through alternate groups such as `uart1`/`uart1b` and `usb2`/`usb2b`, so board states must pick mutually compatible groups. The GPIO mux switch is more nuanced than newer LD11/LD20 logic. Shared input-enable semantics make disabling individual pins risky or unsupported.

## Test Signals

Useful signals include successful probe with `socionext,uniphier-ld4-pinctrl`, pinctrl state tests for eMMC, NAND, SD, MII/RMII Ethernet, system bus chip selects, alternate UART/USB groups, GPIO request tests covering PORT00-PORT26 and XIRQ offsets, verification that dedicated negative-mux pins do not cause register errors, pinconf pull/drive tests, and suspend/resume checks for shared input-enable and mux retention.
