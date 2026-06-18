# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-topckgen.c

## Purpose

This MT7981 topckgen driver builds the main fixed-factor and mux clock tree for networking, storage, peripheral, audio, USB, PCIe, DRAM, AXI/APB, and WED paths.

## Important APIs, types, and functions

Important data includes `top_divs[]`, many `__initconst` parent arrays, `top_muxes[]`, one audio divider composite in `top_aud_divs[]`, and `topck_desc`. The platform driver binds `"mediatek,mt7981-topckgen"` to `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Simple probe registers fixed factors, muxes under `mt7981_clk_lock`, one composite audio divider, and the OF provider. Muxes use clear/set/update register triplets from `0x000` through `0x080`, with update bits at `0x1c0`/`0x1c4`. Critical flags protect `csw_f26m_sel`, `dramc_sel`, `dramc_md32_sel`, `sysaxi_sel`, `sysapb_sel`, and `sgm_reg_sel`. Hardware state persists until reset or CCF operations.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, and MT7981 bindings. It consumes PLLs from apmixed and supplies parents to infracfg, ethsys/SGMII, PCIe, USB, eMMC/NAND, SPI/I2C/UART/PWM, WED MCU, and audio blocks.

## Risks and test signals

Risks include critical clock flag removal, update-bit mistakes, and parent-name mismatch with infracfg/eth. Test boot stability, Ethernet/WED, storage, PCIe/USB, peripheral clocks, audio, and `clk_summary` rate/parent checks.
