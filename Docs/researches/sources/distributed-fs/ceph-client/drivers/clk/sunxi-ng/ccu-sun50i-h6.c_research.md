# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6.c

Purpose: main CCU driver for Allwinner H6. It models PLLs, CPU/bus roots, MBUS, module clocks, bus gates, fixed factors, reset lines, and H6-specific safe register defaults.

Important APIs, types, and functions: major objects include `pll_cpux_clk`, DDR/peripheral/GPU/video/VE/DE/HSIC/audio PLLs, CPU/AXI/PSI/AHB/APB divisors, module clocks for MMC/USB/display/HDMI/CEC/CSI/audio, `sun50i_h6_ccu_clks`, `sun50i_h6_hw_clks`, `sun50i_h6_ccu_resets`, `sun50i_h6_ccu_desc`, and `sun50i_h6_ccu_probe()`.

Control flow: probe maps CCU registers, fixes GPU PLL and GPU clock divider defaults, enables lock bits for all PLLs, clears video PLL output-divider bits, forces OHCI 12 MHz source muxes to a known parent, programs PLL audio post/output dividers for exact audio rates, selects the usable HDMI CEC parent, registers clocks/resets, then installs a CPU mux notifier for PLL CPUX rate changes.

State and persistence: all durable behavior is hardware register state. Static descriptor arrays persist for module lifetime. No runtime allocation beyond devm registration and no filesystem persistence.

Dependencies and integration points: binds `allwinner,sun50i-h6-ccu`, depends on common Sunxi CCU helpers, DT binding IDs, and common clock reset consumers. It is central to CPUfreq, DRAM/MBUS, MMC, USB2/USB3, HDMI/CEC, display engine/TCON, GPU, CSI, VE, and audio blocks.

Risks and test signals: H6 has several explicit hardware quirks: unmodeled PLL test dividers, mysterious OHCI muxes, exact audio SDM rates, and CEC parent selection. Regressions appear as clock rate miscalculation, PLL lock failures, or peripherals hanging. Test signals include clk summary rates, cpufreq stress, HDMI/CEC, USB OHCI/EHCI, MMC, display pipeline, audio 22.5792/24.576 MHz families, reset-controller use, and suspend/resume.
