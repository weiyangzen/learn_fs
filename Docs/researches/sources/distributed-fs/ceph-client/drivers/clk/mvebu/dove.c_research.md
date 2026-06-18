# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove.c

Purpose: Dove early clock setup for SAR-derived core clocks, optional PMU dividers, and peripheral gate clocks.

Important APIs/functions: `dove_clk_init` calls `mvebu_coreclk_setup`, optional `dove_divider_clk_init`, and optional `mvebu_clk_gating_setup`. Helpers decode TCLK, CPU frequency, and CPU-to-L2/DDR ratios from SAR bits.

Control flow: core setup registers `tclk`, `cpuclk`, `l2clk`, and `ddrclk`. The init function searches globally for compatible divider and gating nodes, initializes them if present, and drops node refs. Gate descriptors expose USB, GE/GE PHY, SATA, PCIe, SDIO, NAND, camera, I2S, crypto, AC97, PDMA, and XOR gates.

State and persistence: core rates are fixed from boot straps; divider and gate state are MMIO-backed and managed by their helper providers.

Dependencies and integration: MVEBU common helpers, Dove divider helper, and DT compatibles `marvell,dove-core-clock`, `marvell,dove-divider-clock`, and `marvell,dove-gating-clock`.

Risks: unsupported SAR encodings map to zero rates without central rejection. Global compatible-node search can initialize the first matching node rather than a strict child relation. Divider provider assumes a fixed core PLL rate.

Test signals: Dove board boot, SAR mode rate checks, divider output rates, GE/SATA/USB gate tests, and DT topology tests with multiple compatible nodes.
