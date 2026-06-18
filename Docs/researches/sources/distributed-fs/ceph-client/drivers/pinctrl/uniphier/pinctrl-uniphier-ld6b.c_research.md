# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld6b.c

## Purpose

This source defines the UniPhier LD6b SoC pin controller tables and binding. It feeds LD6b-specific pin descriptors, peripheral mux groups, GPIO ranges, and capability flags into the shared UniPhier pinctrl implementation.

## Important APIs, Types, And Functions

`uniphier_ld6b_pins` contains 235 pin descriptors. The file defines 32 mux groups, 2 GPIO-only groups, and 20 pinmux functions. Notable groups include `adinter` for Achip-Dchip interconnect, eMMC plus 8-bit data extension, RGMII/RMII Ethernet, I2C0-I2C3, NAND plus chip select, SD, SPI0/SPI1, system bus with chip-select groups 1 through 5, UART variants including `uart0b`, `uart1b`, and `uart2b`, and USB0-USB3.

`uniphier_ld6b_get_gpio_muxval()` returns mux value 14 for GPIO offsets 120-143, documented as XIRQ aliases of PORT150-177, and mux value 15 otherwise. `uniphier_ld6b_pindata` uses `.caps = 0`, so it relies on the default mux layout and shared or indexed input-enable semantics rather than per-pin override. The OF compatible is `socionext,uniphier-ld6b-pinctrl`.

## Control Flow

The LD6b built-in platform driver matches its OF compatible and calls `uniphier_pinctrl_probe()`. The shared probe registers the static tables. Runtime mux selection and GPIO request handling are table-driven: selected groups write the listed mux values, while GPIO requests derive a mux value from the LD6b callback. Generic pinconf operations operate on the packed LD6b drive, pull, and input-enable metadata.

## State And Persistence

LD6b state in this file is immutable. Mutable runtime state is owned by the shared core and by hardware registers. Since the capabilities field is zero, suspend/resume save ranges and input-enable behavior are based on the descriptor-encoded register indices, and the debug-mux-separate load strobe is not used.

## Dependencies And Integration Points

The file depends on `pinctrl-uniphier.h`, the common UniPhier core, and Linux platform/OF infrastructure. It exposes function and group names to board DT pinctrl states, and its GPIO mux callback integrates with GPIO ranges registered by the GPIO/pinctrl subsystem.

## Risks

The table has many high-numbered pads and overlapping alternate serial/system-bus chip selects. Wrong mux values on `system_bus_cs*`, UART alternates, or NAND/eMMC shared pads can break boot media or board buses. The XIRQ alias comment means GPIO offsets 120-143 are not independent raw pins; tests must validate the GPIO controller's offset mapping. With `.caps = 0`, individual input-disable requests should fail when controls are shared, so device-tree states must not assume per-pin input disable.

## Test Signals

Validation should cover successful probe, pinmux tests for `adinter`, boot media groups, RGMII/RMII, all system-bus chip selects, alternate UARTs, SPI, SD, and USB0-USB3, GPIO request tests for XIRQ aliases and ordinary GPIOs, pinconf tests on representative drive/pull classes, negative or unsupported input-disable behavior, and suspend/resume restoration of mux, drive, pull, and input-enable registers.
