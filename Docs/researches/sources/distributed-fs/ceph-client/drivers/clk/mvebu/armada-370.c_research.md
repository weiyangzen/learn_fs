# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-370.c

Purpose: Armada 370 early clock setup for SAR-derived core clocks and peripheral gate clocks.

Important APIs/functions: `a370_clk_init` calls `mvebu_coreclk_setup` and optionally `mvebu_clk_gating_setup`. Helpers decode TCLK, CPU frequency, CPU-to-NB/HCLK/DRAM ratios, and SSCG enable state.

Control flow: the core-clock descriptor reads SAR bits to register `tclk`, `cpuclk`, and fixed-factor `nbclk`, `hclk`, and `dramclk`. If a matching gating node exists, gate descriptors register clocks such as audio, PCIe, GE, SATA, SDIO, crypto, TDM, DDR.

State and persistence: clocks are fixed from boot SAR state; gate state is MMIO-backed and restored by common syscore code.

Dependencies and integration: MVEBU common helpers, `kirkwood_fix_sscg_deviation` for spread-spectrum correction, DT compatibles `marvell,armada-370-core-clock` and `marvell,armada-370-gating-clock`.

Risks: unsupported CPU frequency selector returns zero. Gate names and bit indexes are DT ABI-sensitive. Crypto and DDR use `CLK_IGNORE_UNUSED` to avoid unwanted disable.

Test signals: Armada 370 boot rate check, gating node discovery, SSCG-enabled system clock validation, and peripheral enable tests.
