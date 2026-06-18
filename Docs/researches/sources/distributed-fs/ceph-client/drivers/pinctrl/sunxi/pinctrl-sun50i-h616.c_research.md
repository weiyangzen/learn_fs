# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616.c

## Purpose

This file supplies the main Allwinner H616 PIO table for banks PA, PC, PD, PE, PF, PG, PH, and PI. It describes GPIO, mux, IO-bias, and external interrupt capabilities for storage, networking, display, audio, camera, serial, and transport-stream functions.

## Important APIs, Types, And Functions

Important definitions are `h616_pins[]`, `h616_irq_bank_map[]`, `h616_pinctrl_data`, `h616_pinctrl_probe()`, `h616_pinctrl_match[]`, and `h616_pinctrl_driver`. The descriptor uses `ARRAY_SIZE(h616_irq_bank_map)`, maps IRQ banks through `{ 0, 2, 3, 4, 5, 6, 7, 8 }`, enables `irq_read_needs_mux`, and selects `BIAS_VOLTAGE_PIO_POW_MODE_CTL`.

## Control Flow

The built-in driver binds to `allwinner,sun50i-h616-pinctrl` and calls `sunxi_pinctrl_init()` in probe. The common driver registers all pins and translates the non-contiguous IRQ bank map when handling external interrupts.

## State And Persistence

Local state is immutable descriptor data. Runtime state is common-core data plus hardware PIO register contents. IO bias is managed through the PIO power-mode control variant, and interrupt readback depends on mux state.

## Dependencies And Integration Points

The table integrates EMAC0/EMAC1, I2C, I2S, PWM, NAND, MMC, SPI, UART, SIM, SPDIF, DMIC, LCD, LVDS, HDMI, CSI, TCON, TS, clock fanout, IR receive, JTAG, and GPIO interrupt functions. It depends on the shared sunxi pinctrl core.

## Risks

The table is large and has non-contiguous banks, making IRQ bank map correctness critical. H616 has many similarly named functions such as `emac0` versus `emac1` and lane-specific I2S names; spelling or mux-value drift breaks device-tree consumers. IO bias variant differs from H6, so cross-SoC copy/paste can misprogram voltage-domain registers.

## Test Signals

Validate probe, debugfs pin/function output for all banks, GPIO tests on PA/PC-PI, IRQ tests for each mapped bank, IO-bias readback, and peripheral tests for Ethernet, MMC, NAND/SPI, UART, I2C, display, HDMI, audio, camera, TS, and clock fanout pins.
