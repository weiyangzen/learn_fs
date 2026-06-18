# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-xp.c

Purpose: Armada XP early clock setup for SAR-derived core clocks and extensive peripheral gate clocks.

Important APIs/functions: `axp_clk_init` calls `mvebu_coreclk_setup` and optional `mvebu_clk_gating_setup`. Helpers decode split 64-bit SAR fields for CPU frequency and fabric ratios.

Control flow: TCLK is fixed at 250 MHz. CPU frequency selector combines low and high SAR bits; fabric ratio selector also combines non-contiguous bits. The common core helper registers `tclk`, `cpuclk`, `nbclk`, `hclk`, and `dramclk`; gating setup registers GE, PCIe lanes, SATA, LCD, SDIO, USB, XOR, crypto, TDM, and audio clocks.

State and persistence: core clocks are fixed after boot; gates are MMIO-backed.

Dependencies and integration: MVEBU common helper, DT compatibles `marvell,armada-xp-core-clock` and `marvell,armada-xp-gating-clock`, and CPU clock support from `clk-cpu.c` for per-CPU dividers.

Risks: some CPU frequency selectors map to zero. Non-contiguous SAR decoding is easy to regress. Gate hierarchy uses parent gate names for SATA links and ports.

Test signals: Armada XP boot on several strap modes, PCIe/SATA gate tests, CPU divisor provider interaction, and `clk_summary` comparison with board DTS.
