# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun4i-a10.c

## Purpose

This source describes the shared PIO controller for Allwinner A10, A20, and R40-class SoCs. It contains a large pin/function database for banks PA through PI and uses variant flags to expose only the functions valid on each compatible SoC.

## Important APIs, Types, And Functions

Important definitions are `PINCTRL_SUN4I_A10`, `PINCTRL_SUN7I_A20`, `PINCTRL_SUN8I_R40`, `sun4i_a10_pins[]`, `sun4i_a10_pinctrl_data`, `sun4i_a10_pinctrl_probe()`, and `sun4i_a10_pinctrl_match[]`. The table uses `SUNXI_FUNCTION_VARIANT()` heavily alongside regular `SUNXI_FUNCTION()` and `SUNXI_FUNCTION_IRQ_BANK()`.

## Control Flow

The built-in platform driver matches `allwinner,sun4i-a10-pinctrl`, `allwinner,sun7i-a20-pinctrl`, or `allwinner,sun8i-r40-pinctrl`. Probe reads the match data variant bit and calls `sunxi_pinctrl_init_with_flags()`. The common core filters variant-scoped functions and then services pinctrl, GPIO, and IRQ requests using the static descriptor.

## State And Persistence

The file owns only constant data. Runtime pin state is hardware register state plus common-core bookkeeping. The descriptor sets one IRQ bank, `irq_read_needs_mux = true`, and `disable_strict_mode = true`, so the core allows less strict GPIO/mux overlap while still requiring mux-aware IRQ reads.

## Dependencies And Integration Points

The file depends on OF match data and the sunxi common core. It integrates legacy peripherals including EMAC/GMAC, SPI, UART, CAN, I2C, I2S, AC97, IR, HDMI, LCD, LVDS, CSI, TS, MMC, NAND, PATA, memory-stick, PS2, keypad, PWM, JTAG, timers, clock outputs, and debug/pll functions.

## Risks

This is a high-risk table because one source serves three related SoCs. Variant masks must be exact; exposing A20 or R40-only functions on A10 can create unusable device-tree configurations, while hiding shared functions breaks boards. The old interrupt behavior and `disable_strict_mode` are compatibility choices that should not be changed casually. Large bank tables make mux-value transposition errors hard to catch by inspection.

## Test Signals

Validation should include builds and boot probes for all three compatibles, debugfs confirmation of variant-specific functions, GPIO and IRQ tests on PA-PI, and board-level mux tests for UART, MMC, Ethernet, display, camera, NAND/PATA, I2C, SPI, and audio paths.
