# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-39x.c

Purpose: Armada 39x early clock setup with SAR-derived core clocks, optional refclk, and peripheral gates.

Important APIs/functions: `armada_39x_coreclk_init` registers core clocks through `mvebu_coreclk_setup`; `armada_39x_clk_gating_init` registers gates. Helpers decode TCLK, CPU frequency, fixed ratios, and 25/40 MHz refclk.

Control flow: SARL selects CPU/TCLK modes and SARH selects reference clock. Core setup registers `tclk`, `cpuclk`, fixed-factor `nbclk`, `hclk`, `dclk`, and optional `refclk`. Gating registers PCIe, USB3, SATA, SDIO, and XOR gates.

State and persistence: fixed at boot from SAR registers; gates are hardware-backed.

Dependencies and integration: MVEBU common helpers and DT compatibles `marvell,armada-390-core-clock` and `marvell,armada-390-gating-clock`.

Risks: sparse CPU frequency table returns zero for unsupported in-range selectors. Ratios are hard-coded rather than mode-table derived, so future variants need care.

Test signals: refclk strap validation, core clock rate checks, PCIe/SATA/USB gate behavior, and SAR mode boot coverage.
