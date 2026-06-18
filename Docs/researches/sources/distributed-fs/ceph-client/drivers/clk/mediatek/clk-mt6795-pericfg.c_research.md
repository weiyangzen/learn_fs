# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-pericfg.c

## Purpose

This MT6795 pericfg driver exposes peripheral gates, UART source muxes, and a simple reset controller. It supplies clocks for NFI, thermal, PWM, USB, DMA, MSDC, IRDA, UART, I2C, AUXADC, SPI, and the peripheral bus.

## Important APIs, types, and functions

Important data includes `peri_cg_regs`, `peri_clks[]`, `peri_gates[]`, `peri_rst_ofs[]`, `peri_idx_map[]`, `clk_rst_desc`, and `mt6795_peri_clk_lock`. `clk_mt6795_pericfg_probe()` registers resets, gates, composites, and the OF provider; remove reverses composites and gates.

## Control flow, state, and persistence

Probe maps the resource, allocates `CLK_PERI_NR_CLK`, registers reset bank `0x0`, registers gates at set/clear/status offsets `0x8/0x10/0x18`, registers four UART muxes at `0x40c`, and publishes the provider. The spinlock protects composite mux register updates. State is the hardware reset, gate, and mux registers and their CCF objects.

## Dependencies and integration points

Dependencies include `clk-gate.h`, `clk-mtk.h`, `reset.h`, MT6795 clock bindings, and MT6795 reset bindings. It integrates with serial, SPI, I2C, USB, PWM, MMC, NAND, thermal, DMA, and reset consumers. Topckgen parents include `axi_sel`, `usb30_sel`, `usb20_sel`, `msdc50_0_sel`, `msdc30_*_sel`, `irda_sel`, `spi_sel`, and `clk26m`.

## Risks and test signals

Risks include reset-bank map errors, UART mux selection bugs, and gate polarity mistakes. Test by probing UARTs, I2C, SPI, USB, MMC/NAND, thermal, and reset-controlled blocks; also verify `clk_summary` parent choices after changing UART source clocks.
