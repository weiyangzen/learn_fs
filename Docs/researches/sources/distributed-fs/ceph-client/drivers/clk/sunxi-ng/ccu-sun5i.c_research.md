# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.c

Purpose: early CCU driver for Allwinner sun5i A10s/A13/GR8 SoCs. It models legacy PLLs, CPU/AXI/AHB/APB roots, AHB/APB/module gates, display/media/audio/USB/GPS/DRAM clocks, reset lines, and variant-specific exported clock sets.

Important APIs, types, and functions: defines PLLs using `ccu_nkmp`, `ccu_nm`, `ccu_mult`, `ccu_nk`, and fixed factors; many gates and module clocks via Sunxi macros; `sun5i_a10s_ccu_clks`, `sun5i_a10s_hw_clks`, `sun5i_a13_hw_clks`, `sun5i_gr8_hw_clks`, `sun5i_a10s_ccu_resets`, three `sunxi_ccu_desc` structures, `sun5i_ccu_init()`, and three `CLK_OF_DECLARE` setup functions.

Control flow: early OF init maps CCU registers with `of_io_request_and_map()`, forces PLL-Audio-1x divider to 1, reparents AHB to PLL-periph instead of CPU/AXI to avoid cpufreq-induced timer instability, and calls `of_sunxi_ccu_probe()`. A10s, A13, and GR8 share clock objects but expose different `clk_hw_onecell_data` subsets.

State and persistence: state is early-mapped CCU MMIO and static clock descriptors. No devm cleanup exists because registration happens during early boot. Reset state is exposed through mapped reset bits.

Dependencies and integration points: binds through `CLK_OF_DECLARE` for `allwinner,sun5i-a10s-ccu`, `allwinner,sun5i-a13-ccu`, and `nextthing,gr8-ccu`. It integrates with DT binding IDs, common clock/reset frameworks, and consumers for CPU, timers, MMC, NAND, USB, EMAC, display, camera, audio, GPU, VE, and DRAM gates.

Risks and test signals: early mapping failures only log and return, leaving many consumers without clocks. Variant tables intentionally omit unsupported TS/GPS/HDMI/I2S/keypad/SPDIF combinations, so table accuracy matters. AHB reparenting protects timers but changes expected bus parents. Test signals include early boot clock provider availability, cpufreq plus high-speed timer stability, A10s/A13/GR8 peripheral probes, display/audio/USB behavior, reset consumers, and clk summary comparison per variant.
