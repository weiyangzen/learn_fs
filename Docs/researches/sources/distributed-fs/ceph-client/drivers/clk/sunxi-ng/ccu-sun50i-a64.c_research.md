# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.c

Purpose: Allwinner A64 main CCU driver. It describes the SoC clock tree, exported `clk_hw` IDs, bus/module gates, reset lines, and probe-time register normalization for the common clock and reset frameworks.

Important APIs, types, and functions: uses Sunxi CCU primitives such as `ccu_nk`, `ccu_nm`, `ccu_nkm`, `ccu_mp`, `ccu_div`, `ccu_mux`, and `ccu_gate`. The central tables are `sun50i_a64_ccu_clks`, `sun50i_a64_hw_clks`, `sun50i_a64_ccu_resets`, and `sun50i_a64_ccu_desc`. `sun50i_a64_ccu_probe()` maps MMIO, adjusts PLL defaults, calls `devm_sunxi_ccu_probe()`, and registers CPU PLL/mux notifiers.

Control flow: platform probe maps resource 0, forces the audio 1x divider to 1, seeds the MIPI PLL register, registers the descriptor, then wires notifiers so CPU rate changes gate/ungate PLL CPUX and temporarily reparent CPUX to the 24 MHz oscillator.

State and persistence: persistent state is hardware CCU register content. Software state is static descriptor tables plus devm-registered clocks/resets; no disk state exists. Reset mappings are bit offsets in bus reset registers.

Dependencies and integration points: binds `allwinner,sun50i-a64-ccu`, imports `SUNXI_CCU`, includes DT clock/reset bindings through `ccu-sun50i-a64.h`, and supplies clocks/resets consumed by CPUfreq, MMC, USB, display, GPU, CSI, audio, DRAM, and PRCM users.

Risks and test signals: register bit positions are high-risk because most behavior is table-driven. The MIPI PLL magic value and audio divider fixup are hardware assumptions. CPU notifier behavior should be tested with cpufreq transitions. Good signals are boot probe success, complete DT clock lookup coverage, reset deassert for peripherals, `/sys/kernel/debug/clk/clk_summary` rates, MMC/USB/display/audio operation, and suspend/resume sanity.
