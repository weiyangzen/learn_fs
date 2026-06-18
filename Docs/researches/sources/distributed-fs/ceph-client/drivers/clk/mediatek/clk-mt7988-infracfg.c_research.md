# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-infracfg.c

## Purpose

This MT7988 infracfg driver registers infrastructure muxes, gates, and reset lines for UART/SPI/PWM, PCIe, USB, audio, storage, DMA, debug, DRAM, security, and low-speed peripheral paths.

## Important APIs, types, and functions

Important definitions include reset offsets `MT7988_INFRA_RST0_SET_OFFSET` and `MT7988_INFRA_RST1_SET_OFFSET`, `infra_muxes[]`, four gate-register banks, `infra_clks[]`, `infra_rst_desc`, and `infra_desc`. It uses `mtk_clk_simple_probe()`/`remove` for `"mediatek,mt7988-infracfg"`.

## Control flow, state, and persistence

Simple probe registers muxes under `mt7988_clk_lock`, gates across INFRA0-3, and a set/clear reset controller. Muxes select UART, SPI, PWM, and four PCIe TL outputs using register triplets at `0x18/0x10/0x14` and `0x28/0x20/0x24`. Gates use normal set/clear operations across offsets `0x10`, `0x40`, `0x50`, and `0x60`. Reset mapping exposes PEXTP MAC and thermal controller resets. State is hardware mux/gate/reset state and provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, MT7988 clock bindings, and MT7988 reset bindings. Parent clocks come from MT7988 topckgen outputs such as `csw_infra_f26m_sel`, `uart_sel`, `spi_sel`, `spim_mst_sel`, `sysaxi_sel`, `pwm_sel`, `pextp_tl*_sel`, `aud_l_sel`, `a1sys_sel`, `usb_*_sel`, `emmc_*_sel`, and `top_xtal`. Consumers include serial/SPI/PWM, USB, PCIe ports 0-3, storage, audio, DMA, JTAG/debug, and reset users.

## Risks and test signals

Risks include numerous PCIe/USB gate shifts, critical flags on DRAM/debug/NFI/SPI/RTC/USB frame counters, reset index-map errors, and parent-name drift. Test all PCIe ports, USB ports, UART/SPI/PWM, storage, audio, thermal reset, debug/JTAG, and `clk_summary` after idle clock pruning.
