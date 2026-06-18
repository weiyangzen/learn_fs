# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro4.c

## Purpose

This source supplies the UniPhier Pro4 SoC pinctrl tables and platform-driver binding. It is the Pro4 data layer for the shared UniPhier core and includes the debug-mux-separate capability needed by this SoC's pinmux register layout.

## Important APIs, Types, And Functions

`uniphier_pro4_pins` contains 329 pin descriptors, the largest table in this item. It defines 36 mux groups, one GPIO-only group, and 23 functions. Major groups include eMMC and 8-bit data, Ethernet MII/RGMII/RMII plus alternate RMII-B, I2C0-I2C3 and I2C6, NAND plus chip select, SD and SD1, SPI0/SPI1, system bus plus chip-select groups 0 through 7, UART0-UART3 with UART3 flow/modem extensions, and USB0-USB3.

`uniphier_pro4_get_gpio_muxval()` returns mux value 2 for GPIO offsets 134-140, documented as XIRQ14-XIRQ20, and mux value 7 otherwise. `uniphier_pro4_pindata` sets `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`, which changes the shared mux writer to a 4-bit normal/debug split and makes it write `UNIPHIER_PINCTRL_LOAD_PINMUX` after mux changes and after resume. The OF compatible is `socionext,uniphier-pro4-pinctrl`.

## Control Flow

The Pro4 platform driver probes through `uniphier_pro4_pinctrl_probe()` and passes `uniphier_pro4_pindata` to the shared core. Pinctrl state selection uses Pro4 group arrays and mux values. GPIO requests use the Pro4 callback and then the shared one-pin mux setter. Because debug mux is separate, mux writes follow the Pro4-specific register layout path and issue the load strobe.

## State And Persistence

The Pro4 tables are immutable static metadata. Runtime state lives in the shared pinctrl driver and hardware registers. Pro4 does not set per-pin input-enable capability, but does set debug-mux-separate; this affects both normal runtime mux writes and PM resume, where the shared core reloads pinmux after bulk-restoring saved registers.

## Dependencies And Integration Points

Dependencies include `pinctrl-uniphier.h`, the shared UniPhier core, Linux platform/OF infrastructure, syscon/regmap access through the parent node, and board DT pinctrl states. The Pro4 compatible string binds the SoC-specific data into the common implementation.

## Risks

The Pro4 table is large and has many high-numbered pins, system-bus chip selects, and overlapping storage/network interfaces. Descriptor or mux value mistakes can affect boot media, external bus chip selects, or Ethernet modes. `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE` is critical: if omitted, the core would use the wrong mux stride and skip the load-pinmux register; if set incorrectly, other SoCs would be misprogrammed. The GPIO mux policy has a narrow XIRQ14-XIRQ20 exception, so GPIO range offset correctness is essential. Shared input-enable semantics still apply because the per-pin input-enable flag is not set.

## Test Signals

Useful validation includes successful probe with `socionext,uniphier-pro4-pinctrl`, pinmux state tests for eMMC/NAND/SD/SD1, MII/RGMII/RMII/RMII-B Ethernet, SPI, I2C, UART, USB, and every system-bus chip select, GPIO request tests around offsets 134-140 and ordinary offsets, verification that mux writes trigger load-pinmux behavior, pinconf tests across supported drive/pull classes, and suspend/resume tests that confirm mux state is restored and reloaded.
