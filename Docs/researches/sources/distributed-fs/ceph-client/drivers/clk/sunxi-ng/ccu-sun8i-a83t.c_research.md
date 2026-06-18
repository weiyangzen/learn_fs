# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.c

## Purpose

This file implements the Allwinner A83T main CCU. It supports a dual-cluster CPU clock tree, a shared PLL lock register, audio/video/VE/DDR/peripheral/GPU/HSIC/DE/video1 PLLs, AHB/APB buses, AHB2 routing, CCI400, media/display/camera/HDMI/MIPI/GPU clocks, and reset lines.

## Important APIs, types, and functions

Key objects include `pll_c0cpux_clk`, `pll_c1cpux_clk`, `pll_audio_clk`, other PLL `ccu_nkmp` instances using `CCU_FEATURE_LOCK_REG`, cluster muxes `c0cpux_clk` and `c1cpux_clk`, `cci400_clk`, `sun8i_a83t_ccu_clks`, `sun8i_a83t_hw_clks`, and `sun8i_a83t_ccu_resets`. `sun8i_a83t_cpu_pll_fixup()` normalizes CPU PLL P dividers, and `sun8i_a83t_ccu_probe()` is the platform probe for `allwinner,sun8i-a83t-ccu`.

## Control flow, state, and persistence

Probe maps MMIO, enforces audio PLL d1/d2 defaults, runs CPU PLL fixups for both clusters so P is not used, and registers the CCU with `devm_sunxi_ccu_probe()`. The fixup lowers N to reset value 17 before clearing P if the P divider was active, avoiding a sudden over-rate. State is contained in CCU registers and registered clock/reset providers.

## Dependencies and integration points

The driver uses ccu mult/nkmp/nm/mp/mux/div/gate/phase/reset helpers and the A83T dt bindings. It integrates with SMP/cpufreq, CCI400, EMAC/EHCI/OHCI/USB HSIC, MMC/NAND/SPI, audio I2S/TDM/SPDIF, display TCON/HDMI/MIPI DSI, CSI/MIPI CSI, VE, GPU, MBUS, and reset consumers.

## Risks and test signals

The largest risks are CPU PLL modeling simplifications, shared lock-register bit mapping, AHB2 predivider behavior, and `usb-hsic-12m` predivider modeling. Test both CPU clusters under cpufreq, validate CCI400 remains critical, boot display/HDMI/MIPI/CSI paths, exercise USB/EMAC/MMC/audio, and inspect `clk_summary` for lock-backed PLLs and expected parent rates.
