# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-infracfg.c

## Purpose

This MT7986 infracfg driver registers infrastructure factor, mux, and gate clocks for peripherals, storage, USB, PCIe, audio, EIP97, TRNG, DMA, and security/debug paths.

## Important APIs, types, and functions

Important definitions include `infra_divs[]`, parent arrays for UART/SPI/PWM/PCIe, `infra_muxes[]`, gate banks `infra0_cg_regs` through `infra2_cg_regs`, `infra_clks[]`, and `infra_desc`. It is descriptor-based via `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Simple probe registers `infra_sysaxi_d2`, muxes under `mt7986_clk_lock`, gates across three banks, and the OF provider. Muxes use register triplets at `0x18/0x10/0x14` and `0x28/0x20/0x24`; gates use normal set/clear banks at `0x40`, `0x50`, and `0x60`. State is hardware mux/gate settings and CCF provider data.

## Dependencies and integration points

Dependencies include MT7986 clock bindings, `clk-mux.h`, `clk-gate.h`, and `clk-mtk.h`. Parent clocks come from MT7986 topckgen, including `sysaxi_sel`, `csw_f26m_sel`, `eip_b_sel`, `u2u3_sys_sel`, `u2u3_sel`, `pextp_tl_ck_sel`, and storage/audio/peripheral parents. Consumers include UART/SPI/I2C/PWM, eMMC/NAND, USB, PCIe, EIP97 crypto, audio, and DMA.

## Risks and test signals

Risks include mux parent mismatch, update-bit mistakes, and gate shifts for storage/USB/PCIe/security. Test all low-speed buses, storage, PCIe, USB, crypto, TRNG, audio, and `clk_summary`.
