# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.c

## Purpose

This file implements PRCM/R-domain CCU support for A83T, H3, and A64-class SoCs. It provides AR100, AHB0/APB0, APB0 peripheral gates, IR module clock variants, and reset lines in the low-power domain.

## Important APIs, types, and functions

Key definitions are `ar100_clk`, fixed-factor `ahb0_clk`, `apb0_clk`, APB0 gate clocks, generic `ir_clk`, A83T-specific `a83t_ir_clk`, per-variant `clk_hw_onecell_data`, reset maps, and descriptors. `sun8i_r_ccu_probe()` selects descriptor data by compatible and calls `devm_sunxi_ccu_probe()`.

## Control flow, state, and persistence

Probe only fetches match data, maps MMIO, and registers the selected descriptor. Variant data changes which IR clock implementation and which APB0 gates/resets are exported. State is register-backed clock/reset state in the PRCM block.

## Dependencies and integration points

The file depends on OF/platform APIs and sunxi-ng div/gate/mp/nm/reset helpers. It consumes firmware-named parents such as `losc`, `hosc`, `pll-periph`, and `iosc`, and provides clocks for AR100 firmware/remote processor paths, PIO, IR, timers, RSB, UART, I2C, and TWD consumers.

## Risks and test signals

Risks include variant mismatches in APB0_RSB availability, A83T IR fixed predivider behavior, and parent-name requirements from firmware. Test on all three compatibles, check AR100 rate selection, IR carrier rates, RSB/I2C/UART low-power peripherals, reset assertions, and suspend/resume low-power-domain behavior.
