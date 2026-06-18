# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.c

## Purpose

This is the large main CCU provider for the Allwinner R40. It models CPU/audio/video/VE/DDR/peripheral/SATA/GPU/MIPI/DE PLLs, 12 MHz derived oscillator, bus fabric, a broad peripheral gate set, storage/module clocks, SATA and GMAC-related clocking, USB, IR, DRAM/MBUS, display/TV/camera/media clocks, external outputs, resets, and a constrained regmap for GMAC configuration.

## Important APIs, types, and functions

Important objects include `pll_cpu_clk`, `pll_audio_base_clk`, video/VE/DDR/peripheral/SATA/GPU/MIPI/DE PLL clocks, `pll_periph0_sata_clk`, `pll_sata_out_clk`, `cpu_clk`, bus gates, module clocks, `sun8i_r40_ccu_clks`, fixed-factor clocks, `sun8i_r40_hw_clks`, `sun8i_r40_ccu_resets`, and `sun8i_r40_ccu_desc`. The probe is `sun8i_r40_ccu_probe()`. CPU transition helpers are `sun8i_r40_pll_cpu_nb` and `sun8i_r40_cpu_nb`. GMAC integration uses `sun8i_r40_ccu_regmap_accessible_reg()` and `sun8i_r40_ccu_regmap_config`.

## Control flow, state, and persistence

Probe maps MMIO, forces PLL-Audio-1x divider to 1, forces PLL-MIPI to MIPI mode, forces OHCI 12 MHz parent selection to 12 MHz divided from 48 MHz, writes the keyed SYS 32 kHz parent selection to use RTC LOSC output, creates a devm regmap exposing only the GMAC config register, registers the CCU, and installs CPU PLL/mux notifiers for rate changes. State is hardware register state, a devm regmap, and CCF/reset providers.

## Dependencies and integration points

The driver depends on sunxi-ng CCU helpers, Linux regmap, and R40 dt bindings. It integrates with cpufreq, GMAC/dwmac-sun8i via restricted regmap, SATA, USB PHY/OHCI/EHCI/OTG, MMC/NAND/SPI/TS/CE, display engine, TCON LCD/TV, TVE/TVD, HDMI, DSI DPHY, CSI0/CSI1, GPU, codec/I2S/AC97/SPDIF, THS/keypad/IR, I2C/UART/CAN/SCR/PS2, DRAM/MBUS, and reset consumers.

## Risks and test signals

Risk areas are numerous: TODO PLL constraint ranges are not fully encoded, MIPI HDMI mode is unsupported, OHCI and SYS 32 kHz force-writes must match board expectations, the GMAC regmap intentionally exposes only one register, and critical DRAM/MBUS/CPU paths must stay enabled. Test with R40 boot, cpufreq transitions, SATA, GMAC, USB port matrix, display/TV/HDMI/CSI, audio clocks, MMC/storage, thermal/keypad/IR, reset consumers, and regmap access from the Ethernet driver.
