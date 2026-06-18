# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.c

## Purpose

This file provides the main CCU for Allwinner H3 and H5. It models CPU/audio/video/VE/DDR/peripheral/GPU/DE PLLs, bus fabric, AHB2, peripheral bus gates, THS, storage/module clocks, USB gates, H3/H5-specific DRAM clock handling, display/camera/media clocks, MBUS, GPU, and resets.

## Important APIs, types, and functions

Key tables are `sun8i_h3_ccu_clks`, `sun8i_h3_hw_clks`, `sun50i_h5_hw_clks`, `sun8i_h3_ccu_resets`, `sun50i_h5_ccu_resets`, `sun8i_h3_ccu_desc`, and `sun50i_h5_ccu_desc`. The entry point `sun8i_h3_ccu_probe()` selects descriptor data from `of_device_get_match_data()`. CPU rate-change helpers are `sun8i_h3_pll_cpu_nb` and `sun8i_h3_cpu_nb`.

## Control flow, state, and persistence

Probe maps MMIO, forces the audio PLL 1x divider to 1, registers the selected H3/H5 descriptor, then registers a PLL notifier to gate/ungate CPU PLL after rate changes and a mux notifier to reparent CPUX to the 24 MHz oscillator during changes. H3 uses a fixed-factor `dram` clock because its MDFS hardware is broken; H5 uses a real mux/divider. Runtime state is CCU register bits and devm-managed CCF/reset providers.

## Dependencies and integration points

The file depends on sunxi-ng CCU primitives and H3/H5 clock/reset bindings. It feeds cpufreq, DRAM/MBUS, USB PHY/OHCI/EHCI/OTG, EMAC/EPHY, MMC/NAND/SPI/TS/CE, THS, I2C/UART/SCR, I2S/SPDIF/codec, VE, display engine/TCON/TVE/HDMI/deinterlace, CSI, and GPU users.

## Risks and test signals

Important risks are H3 versus H5 onecell differences, the H3 fixed DRAM workaround, reset map differences such as SCR1 on H5, CPU rate-change notifier coverage, and audio PLL simplification. Test both H3 and H5 boot, cpufreq, Ethernet, USB port matrix, MMC tuning, thermal sensor clocking, display/HDMI/TVE, and idle clock disabling.
