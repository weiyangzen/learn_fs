# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-infracfg.c

## Purpose

This MT7981 infracfg driver registers infrastructure factor, mux, and gate clocks for low-speed peripherals, storage, USB, PCIe, audio, DMA, security, and debug paths.

## Important APIs, types, and functions

Important definitions include `infra_divs[]`, parent arrays for UART/SPI/PWM/PCIe muxes, `infra_muxes[]`, three gate-register banks, `infra_clks[]`, and `infracfg_desc`. The driver is descriptor-based with `mtk_clk_simple_probe()`/`remove`.

## Control flow, state, and persistence

The simple probe registers one fixed factor `infra_66m_mck`, muxes protected by `mt7981_clk_lock`, and gates across INFRA0-2. Muxes use clear/set/update offsets such as `0x18/0x10/0x14` and `0x28/0x20/0x24`. Gates use normal set/clear banks at `0x40`, `0x50`, and `0x60`. State is CCF provider registration and hardware mux/gate bits.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, and MT7981 bindings. Parent clocks come from topckgen, including `sysaxi`, `csw_f26m_sel`, `uart_sel`, `spi_sel`, `spim_mst_sel`, `pwm_sel`, `pextp_tl_ck_sel`, storage, USB, audio, and RTC paths. Consumers include UART/SPI/I2C/PWM, eMMC/NAND, USB, PCIe, audio, security, and DMA drivers.

## Risks and test signals

Risks include mux parent mismatch, update-bit omissions, and gate shifts for storage/USB/PCIe. Test serial/SPI/I2C/PWM, eMMC/NAND, PCIe, USB, audio, and clock summary parent selection.
