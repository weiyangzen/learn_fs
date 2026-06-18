# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate.c

Purpose: legacy 32-bit SoCFPGA gate-clock helper.

Important APIs/types/functions: `socfpga_clk_get_parent()`, `socfpga_clk_set_parent()`, `socfpga_clk_get_div()`, `socfpga_clk_recalc_rate()`, `socfpga_clk_determine_rate()`, and `socfpga_gate_init()`.

Control flow: allocates gate state, duplicates ops, parses DT gate/divider/fixed-divider data, disables parent ops for single-parent clocks, registers a clock, and publishes a simple provider.

State and persistence behavior: per-clock gate/divider metadata and hardware source/gate/divider registers; uses global `clk_mgr_base_addr`.

Dependencies/integration points: legacy PLL base mapping, shared `clk.h`, CCF, and DT properties.

Risks: parent handling is name-based; GPIO_DB divider detection uses a fragile pointer/offset bit test; init ordering requires mapped clock-manager base.

Test signals: legacy SoCFPGA boot, parent switching for L4/MMC/NAND/QSPI, divider-rate checks, and one-parent op disabling.
