# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph.c

Purpose: legacy SoCFPGA peripheral clock helper.

Important APIs/types/functions: `clk_periclk_recalc_rate()`, `clk_periclk_get_parent()`, `__socfpga_periph_init()`, and `socfpga_periph_init()`.

Control flow: DT init allocates clock state, points it at the clock manager register, parses optional divider and fixed-divider properties, fills parents, registers a CCF clock, and adds a simple provider.

State and persistence behavior: per-clock divider metadata; parent bit from `CLKMGR_DBCTRL`; hardware clock register controls final divider.

Dependencies/integration points: global `clk_mgr_base_addr`, shared `clk.h`, CCF, and OF clock properties.

Risks: parent get is tied to legacy DBCTRL bit 0; init ordering requires PLL mapping; DT divider fields drive rate correctness.

Test signals: legacy DT boot, peripheral rate verification, parent bit changes, and provider registration.
