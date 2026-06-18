# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-mmp2.c

Purpose: early OF clock initialization for Marvell MMP2 and MMP3, registering PLLs, fixed factors, APBC/APMU peripheral clocks, resets, and generic power domains.

Important APIs/functions: `mmp2_clk_init` is registered for `marvell,mmp2-clock` and `marvell,mmp3-clock`. `mmp2_main_clk_init`, `mmp2_apb_periph_clk_init`, `mmp2_axi_periph_clk_init`, `mmp2_clk_reset_init`, and `mmp2_pm_domain_init` split setup by controller area.

Control flow: init detects MMP2 versus MMP3 compatible, maps MPMU/APMU/APBC resources, registers PM domains, creates the onecell clock table, then registers root PLL/fixed-factor clocks, APB mux/gates, AXI/APMU mix/mux/div/gates, SoC-specific GPU/thermal/SDH additions, and APBC reset cells.

State and persistence: the allocated `mmp2_clk_unit` persists for the lifetime of the system. Clock and reset state is MMIO-backed; PM-domain state is represented by generic PM domains over APMU power island bits.

Dependencies and integration: uses `clk.h`, `reset.h`, MMP2/MMP3 clock and power DT bindings, CCF registration helpers, reset-controller integration, and genpd.

Risks: early-init allocations and MMIO mappings are mostly permanent; some failure paths unmap resources but not all intermediate registrations. A table entry in `mmp3_pll_clks` uses `MMP2_CLK_PLL2` for `"pll1"`, which deserves careful DT binding validation. Shared SDH mix clock setup uses the SDH0 register for all SDH clocks.

Test signals: boot on both MMP2 and MMP3 DTs, clock ID lookup for exported bindings, reset control for APBC devices, GPU/audio/camera genpd on/off, and `clk_summary` hierarchy comparison against expected PLL trees.
