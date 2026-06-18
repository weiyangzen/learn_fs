# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-topckgen.c

## Purpose

This MT7986 topckgen driver provides fixed clocks, fixed factors, and muxes for storage, SPI/I2C/UART/PWM, PCIe, eMMC, DRAM, AXI/APB, debug, networking, SGMII, audio, USB, and AP2CNN host paths.

## Important APIs, types, and functions

Important objects are `top_fixed_clks[]`, `top_divs[]`, parent arrays, `top_muxes[]`, and `topck_desc`. The driver uses `mtk_clk_simple_probe()` for `"mediatek,mt7986-topckgen"`.

## Control flow, state, and persistence

Simple probe registers fixed clocks `top_xtal` and `top_jtag`, fixed factors, muxes under `mt7986_clk_lock`, and the OF provider. Muxes use clear/set/update register triplets from `0x000` through `0x090` with update bits in `0x1c0`/`0x1c4`. Critical flags protect DRAM, DRAMC MD32, SYSAXI, SYSAPB, SGM register, and F26M selections. State is hardware mux settings and CCF registration.

## Dependencies and integration points

Dependencies are MT7986 bindings and MediaTek mux/gate helpers. It consumes apmixed PLLs and supplies parent clocks to infracfg, Ethernet/SGMII, USB, PCIe, eMMC/NAND, SPI/I2C/UART/PWM, WED, audio, and crypto.

## Risks and test signals

Risks include critical-clock flag loss, parent naming drift with infracfg/eth, and wrong update bits. Test boot, storage, network/WED, USB/PCIe, peripheral buses, and clock summary rates.
